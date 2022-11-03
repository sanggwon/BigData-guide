import asyncio
import os
# 웹 소켓 모듈을 선언한다.
import websockets
from pydub import AudioSegment
from pydub.silence import split_on_silence
import shutil
import youtube_dl
import ffmpeg
import speech_recognition as sr 
import nest_asyncio
import time

nest_asyncio.apply()

# 클라이언트 접속이 되면 호출된다.
async def accept(websocket, path):  
    while True:    
        # 클라이언트로부터 메시지를 대기한다.
        url = await websocket.recv()
        print("receive : " + url)

        file_name = url[url.index('watch?v=')+8:]

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'youtube/' + file_name + '.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'progress_hooks': [my_hook],
        }

        input_file_name = 'youtube/' + file_name + '.m4a'
        output_file_name = 'youtube/' + file_name + '.wav'
        folder_name = 'youtube/' + file_name + '-audio-chunks'

        # 클라인언트로 echo를 붙여서 재 전송한다. 

        if not os.path.exists(output_file_name):
            await websocket.send('================== 다운로드 시작 ==================')
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                stream = ffmpeg.input(input_file_name)
                stream = ffmpeg.output(stream, output_file_name)

        await websocket.send('================== 다운로드 완료 ==================')

        r = sr.Recognizer()
        sound = AudioSegment.from_wav(output_file_name)  
        chunks = split_on_silence(sound,
            min_silence_len = 500,
            silence_thresh = sound.dBFS-14,
            keep_silence=500,
        )
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        whole_text = ""
        for i, audio_chunk in enumerate(chunks, start=1):
            file_len = len(chunks)
            percent = round(i / file_len * 100)
            chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
            audio_chunk.export(chunk_filename, format="wav")
            await websocket.send('================== 음성인식 진행률 : ' + str(percent) + '% ==================')
            with sr.AudioFile(chunk_filename) as source:
                audio_listened = r.record(source)
                try:
                    text = r.recognize_google(audio_listened, language='ko-KR')
                except sr.UnknownValueError as e:
                    print("Error:", str(e))
                else:
                    text = f"{text.capitalize()}. "
                    print(chunk_filename, ":", text)
                    await websocket.send(text)
                    whole_text += text

        if os.path.exists(folder_name):
            shutil.rmtree(folder_name)

        await websocket.send('완료')
        time.sleep(1)
        await websocket.send(whole_text)
        # return whole_text

def my_hook(d):
    if d['status'] == 'finished':
        file_tuple = os.path.split(os.path.abspath(d['filename']))
        asyncio.get_event_loop().run_until_complete(finished())
        print("Done downloading {}".format(file_tuple[1]))
        
    if d['status'] == 'downloading':
        asyncio.get_event_loop().run_until_complete(connect(d))
        print(d['filename'], d['_percent_str'], d['_eta_str'])

async def connect(d):  
    # 웹 소켓에 접속을 합니다.  
    async with websockets.connect("ws://192.168.0.204:8083/WebSocketService") as websocket:
        await websocket.send(d['filename'] + d['_percent_str']+ d['_eta_str'])

async def finished():
    # 웹 소켓에 접속을 합니다.  
    async with websockets.connect("ws://192.168.0.204:8083/WebSocketService") as websocket:
        await websocket.send('완료')

if not os.path.isdir('youtube'):
    os.mkdir('youtube')

# 웹 소켓 서버 생성.호스트는 localhost에 port는 9998로 생성한다. 
start_server = websockets.serve(accept, "192.168.0.204", 8085)
# 비동기로 서버를 대기한다.
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()