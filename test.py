import os
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH
from yt_dlp import YoutubeDL

# --- ⚙️ 설정 ---
# ⚠️ 여기에 변환하고 싶은 YouTube URL을 입력하세요.
YOUTUBE_URL = "https://youtu.be/O4uK122HJXg" # 예시 URL
OUTPUT_DIR = r"output_midi_files"
DOWNLOAD_DIR = r"downloaded_audio"
TEMP_FILENAME = "youtube_download" # 다운로드할 임시 파일 이름 (확장자 제외)

# --- 1. 디렉터리 준비 ---
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# --- 2. YouTube > MP3 다운로드 함수 ---
def download_youtube_to_mp3(url, output_path, filename_base):
    """
    YouTube URL에서 오디오를 추출하여 MP3 파일로 저장합니다.
    """
    full_output_path = os.path.join(output_path, filename_base)
    
    # yt-dlp 설정
    ydl_opts = {
        'format': 'bestaudio/best', # 최고의 오디오 품질 선택
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3', # MP3로 인코딩
            'preferredquality': '192', # 오디오 품질 (192kbps)
        }],
        # 파일 저장 경로와 이름 설정. '%(title)s.%(ext)s' 대신 고정된 이름 사용
        'outtmpl': full_output_path, 
        'noplaylist': True, # 재생목록 다운로드 방지
        'quiet': True, # 콘솔 출력 최소화
    }

    try:
        print(f"✅ YouTube 오디오 다운로드 시작: {url}")
        with YoutubeDL(ydl_opts) as ydl:
            # 다운로드 실행 및 파일 정보 추출
            info_dict = ydl.extract_info(url, download=True)
            
            # 다운로드된 파일의 실제 확장자 (여기서는 mp3)를 확인
            # outtmpl 설정에 따라 파일 이름이 'youtube_download.mp3' 형태로 저장됨
            actual_filename = f"{filename_base}.mp3"
            downloaded_mp3_path = os.path.join(output_path, actual_filename)
            
            if os.path.exists(downloaded_mp3_path):
                print(f"✅ 다운로드 완료: {downloaded_mp3_path}")
                return downloaded_mp3_path
            else:
                # outtmpl 설정이 복잡한 경우, 실제 저장된 파일을 찾기 위한 로직 (옵션)
                # yt-dlp는 outtmpl에 파일 이름만 있어도 확장자를 붙여서 저장합니다.
                # 단순화를 위해 고정된 파일 이름을 사용했습니다.
                print("⚠️ 다운로드된 파일을 찾을 수 없습니다. (yt-dlp 내부 처리 문제일 수 있음)")
                return None
                
    except Exception as e:
        print(f"❌ YouTube 다운로드 중 오류 발생: {e}")
        return None

# --- 3. 변환 실행 함수 ---
def convert_mp3_to_midi(mp3_path, output_dir):
    """
    Basic-Pitch 모델을 사용하여 MP3 파일을 MIDI로 변환합니다.
    """
    if not mp3_path or not os.path.exists(mp3_path):
        print("❌ 유효한 MP3 파일 경로가 아닙니다. MIDI 변환을 건너뜁니다.")
        return

    print(f"\n🎵 MIDI 변환 시작: {mp3_path}")
    
    # 모델 경로 준비
    basic_pitch_model_path = str(ICASSP_2022_MODEL_PATH)

    try:
        predict_and_save(
            [mp3_path], # ⬅️ 수정: 'audio_paths=' 키워드를 제거하고 리스트를 첫 번째 위치 인수로 전달
            output_directory=output_dir, 
            save_model_outputs=False, 
            save_notes=True, 
            model_or_model_path=basic_pitch_model_path,
            save_midi=True, 
            sonify_midi=False 
        )
        # Basic-Pitch는 입력 파일 이름 기반으로 MIDI 파일을 생성합니다.
        print(f"✅ 변환 완료. '{output_dir}' 폴더를 확인하세요.")
        
    except Exception as e:
        print(f"❌ Basic-Pitch 변환 중 오류 발생: {e}")

# --- 4. 메인 실행 ---
if __name__ == "__main__":
    
    # 1. YouTube 다운로드
    input_mp3_path = download_youtube_to_mp3(YOUTUBE_URL, DOWNLOAD_DIR, TEMP_FILENAME)
    
    # 2. MIDI 변환
    if input_mp3_path:
        convert_mp3_to_midi(input_mp3_path, OUTPUT_DIR)
        
        # 3. (선택) 임시 다운로드 파일 정리
        try:
            os.remove(input_mp3_path)
            print(f"✨ 임시 다운로드 파일 정리 완료: {input_mp3_path}")
        except Exception as e:
            print(f"⚠️ 임시 파일 정리 실패: {e}")