import asyncio
from fastapi import FastAPI , APIRouter, Request
from fastapi.responses import  JSONResponse ,HTMLResponse ,StreamingResponse
from Workers import process_video_to_frames,frame_reader
from Models import StreamModel
from Controlers import StreamShow,ROI_Selection
from threading import Thread
import cv2




StreamReadingRoute = APIRouter(
    prefix="/Video_Preparation",
    tags=["Video_loading"]
)
@StreamReadingRoute.post("/")
async def StreamReading(request:Request,stream:str):
    manager = StreamModel(request.app.db_client)
    cap = cv2.VideoCapture(stream)
    ret, frame = cap.read()
    if not ret:
        return JSONResponse(content={"message": "Not a real video"}, status_code=404)
    search_result =await manager.search_for_stream( stream_name = stream)
    img = cv2.resize(frame, (960, 608))
    region = ROI_Selection(img)

    if not search_result:
        print(50)
        ROI_Selection_thread = Thread(target=region.main, daemon=True)
        ROI_Selection_thread.start()
        ROI_Selection_thread.join()

    exist , result= await manager.search_and_insert_if_not_exists(stream,ROI=region.points)
    if  not exist:
        frame_queue = result["queue_name"]
        process_video_to_frames.delay(stream=stream,  queue_name = frame_queue )
        frame_reader.delay(frame_queue,regoin_of_interst = region.points)
    if result["status"] == "processing":
        print(result['Tcp_socket'])
    if result['status'] == "finished":
        pass
    return  JSONResponse(content = {"message":"stram reading in progress"},status_code=200)




@StreamReadingRoute.get("/stream/")
async def ShowStream(request: Request,stream:str):
    manager = StreamModel(request.app.db_client)
    result = {"status":"pending"}
    while result['status'] == 'pending':
        exist, result = await manager.search_and_insert_if_not_exists(stream)
        await  asyncio.sleep(.05)
       # print(result)

    if result['status']=='processing':
        port= result["Tcp_socket"]
        stream = StreamShow(PORT=port )
    else :
        return  JSONResponse(content = {"message":
                                            "This stream is not available"},status_code=404)

    async def mjpeg_generator():
        try:
            for frame_bytes in stream.main():
                if await request.is_disconnected():
                    print("Client disconnected")
                    break

                yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                )
        except Exception as e:
            print(f"Stream error: {e}")
        finally:
            print("Cleaning up stream resources")
            stream.client.close()

    return StreamingResponse(
        mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )





@StreamReadingRoute.get("/", response_class=HTMLResponse)
async def stream_interface():
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Large Stream Viewer</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #f4f4f4;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 6px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }

        h2 {
            text-align: center;
            margin-bottom: 20px;
            font-size: 24px;
        }

        .input-group {
            display: flex;
            margin-bottom: 20px;
            justify-content: center;
        }

        .input-group input {
            flex: 1;
            max-width: 800px;
            padding: 10px;
            font-size: 16px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }

        .input-group button {
            padding: 10px 20px;
            margin-left: 10px;
            font-size: 16px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        .input-group button:hover {
            background: #0056b3;
        }

        #message {
            text-align: center;
            font-size: 16px;
            margin-bottom: 15px;
            color: #555;
        }

        .video-container {
            text-align: center;
        }

        #videoStream {
            width: 1280px;
            height: 880px;
            background: #000;
            object-fit: contain;
            display: none;
        }

        .placeholder {
            width: 1280px;
            height: 880px;
            background: #333;
            color: #ccc;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            font-size: 18px;
        }

        @media (max-width: 1400px) {
            #videoStream,
            .placeholder {
                width: 100%;
                height: auto;
                max-width: 1280px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🎥 Large Stream Viewer</h2>
        <div class="input-group">
            <input type="text" id="streamInput" placeholder="Enter stream URL or path">
            <button onclick="startStream()">Start Stream</button>
        </div>
        <div id="message">Ready to stream</div>
        <div class="video-container">
            <div id="videoPlaceholder" class="placeholder">Video will appear here</div>
            <img id="videoStream" />
        </div>
    </div>

    <script>
        function setMessage(text) {
            document.getElementById('message').textContent = text;
        }

        async function startStream() {
            const stream = document.getElementById('streamInput').value.trim();
            if (!stream) {
                setMessage('❌ Please enter a stream URL');
                return;
            }

            setMessage('Starting stream...');
            try {
                let res = await fetch('/Video_Preparation/?stream=' + encodeURIComponent(stream), {
                    method: 'POST'
                });
                if (!res.ok) throw new Error(`HTTP ${res.status}`);

                let data = await res.json();
                setMessage(`✅ ${data.message}`);

                const img = document.getElementById('videoStream');
                const placeholder = document.getElementById('videoPlaceholder');

                img.onload = function() {
                    placeholder.style.display = 'none';
                    img.style.display = 'block';
                };

                img.onerror = function() {
                    setMessage('❌ Failed to load stream');
                    placeholder.style.display = 'flex';
                    img.style.display = 'none';
                };

                img.src = '/Video_Preparation/stream/?stream=' + encodeURIComponent(stream);

            } catch (err) {
                console.error(err);
                setMessage(`❌ Error: ${err.message}`);
            }
        }

        document.getElementById('streamInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') startStream();
        });
    </script>
</body>
</html>

    
    """
    return HTMLResponse(content=html_content)
