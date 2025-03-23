import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox, QComboBox
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

class VideoTranscriptApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('YouTube Video Transcript')  # 윈도우 제목 설정
        layout = QVBoxLayout()

        self.label = QLabel('Enter YouTube URL:')  # 유튜브 URL 입력 레이블
        layout.addWidget(self.label)

        self.url_input = QLineEdit()  # URL 입력 필드
        layout.addWidget(self.url_input)

        self.language_label = QLabel('Select Subtitle Language:')  # 자막 언어 선택 레이블
        layout.addWidget(self.language_label)

        self.language_combo = QComboBox()  # 자막 언어 선택 콤보 박스
        layout.addWidget(self.language_combo)

        self.fetch_button = QPushButton('Fetch Transcript')  # 스크립트 가져오기 버튼
        self.fetch_button.clicked.connect(self.fetch_transcript)
        layout.addWidget(self.fetch_button)

        self.transcript_label = QLabel('Full Transcript:')  # 전체 스크립트 레이블
        layout.addWidget(self.transcript_label)

        self.transcript_text = QTextEdit()  # 전체 스크립트 텍스트 필드
        self.transcript_text.setReadOnly(True)
        layout.addWidget(self.transcript_text)

        self.clear_button = QPushButton('Clear')  # 초기화 버튼
        self.clear_button.clicked.connect(self.clear_text)
        layout.addWidget(self.clear_button)

        self.setLayout(layout)

    def fetch_available_languages(self, video_id):
        # 사용할 수 있는 자막 언어 목록을 가져옴
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            self.language_combo.clear()
            for transcript in transcript_list:
                self.language_combo.addItem(transcript.language, transcript.language_code)
        except TranscriptsDisabled:
            QMessageBox.critical(self, "Error", "Transcripts are disabled for this video.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def fetch_transcript(self):
        # 유튜브 URL에서 비디오 ID를 추출하고 전체 자막을 가져옴
        url = self.url_input.text()
        video_id = self.extract_video_id(url)
        if not video_id:
            QMessageBox.critical(self, "Error", "Invalid YouTube URL")
            return

        selected_language_code = self.language_combo.currentData()
        if not selected_language_code:
            QMessageBox.critical(self, "Error", "Please select a subtitle language.")
            return

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[selected_language_code])
            self.transcript_text.setText(self.format_full_transcript(transcript))
        except NoTranscriptFound:
            QMessageBox.critical(self, "Error", "No transcript found for this video.")
        except TranscriptsDisabled:
            QMessageBox.critical(self, "Error", "Transcripts are disabled for this video.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def extract_video_id(self, url):
        # 유튜브 URL에서 비디오 ID를 추출
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1]
        else:
            return None

    def format_full_transcript(self, transcript):
        # 전체 스크립트를 형식에 맞게 변환
        full_transcript = []
        for entry in transcript:
            start_time = entry['start']
            text = entry['text']
            full_transcript.append(f"({self.format_time(start_time)}) {text}")
        return "\n".join(full_transcript)

    def format_time(self, seconds):
        # 시간을 분:초 형식으로 변환
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02}:{seconds:02}"

    def clear_text(self):
        # 입력 필드와 결과 필드 초기화
        self.url_input.clear()
        self.transcript_text.clear()

    def load_languages(self):
        # URL이 변경될 때마다 사용 가능한 자막 언어 목록을 로드
        url = self.url_input.text()
        video_id = self.extract_video_id(url)
        if video_id:
            self.fetch_available_languages(video_id)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VideoTranscriptApp()
    ex.show()

    # URL 입력이 변경될 때마다 언어 목록 로드
    ex.url_input.textChanged.connect(ex.load_languages)

    sys.exit(app.exec_())
