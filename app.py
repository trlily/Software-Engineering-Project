import os
import pandas as pd

from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

from ml import  main as A


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 제한

# def load_emoji_mapping():
#     df = pd.read_csv('emotion_db.csv')
#     emotions = {'happy': '😄', 'normal': '😐', 'sad': '😢', 'upset': '😠'}

#     emoji_mapping = {}
#     for _, row in df.iterrows():
#         dominant = row[['happy', 'normal', 'sad', 'upset']].astype(int).idxmax()
#         size = int(row[dominant]) * 10 + 10
#         emoji_mapping[row['Data']] = {'emoji': emotions[dominant], 'size': size}
#     return emoji_mapping

def load_emoji_mapping():
    import pandas as pd

    df = pd.read_csv('emotion_db.csv')
    emotions = {'happy': '😄', 'neutral': '😐', 'sad': '😢', 'upset': '😠'}

    emoji_mapping = {}
    for _, row in df.iterrows():
        region = row['Data']
        emoji_mapping[region] = []

        for emotion, emoji in emotions.items():
            count = int(row[emotion])
            if count > 0:
                emoji_mapping[region].append({
                    'emoji': emoji,
                    'size': count * 7 + 10  # 감정 수치에 따라 크기 조정
                })

    return emoji_mapping

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('photo')
        user_text = request.form.get('user_input')  #

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # 예: 텍스트도 모델 함수에 함께 전달 가능
            if filepath.endswith('.jpg') or filepath.endswith('.png'):
                result = A(filepath)  # 또는 A(filepath, user_text) 처럼 활용
                result = result.lower()
                if result not in ['happy', 'neutral', 'sad', 'upset']:
                    result = 'none'
                else:
                    try:
                        db = pd.read_csv('emotion_db.csv')
                        emotion_key = result.lower()
                        valid_emotions = ['happy', 'neutral', 'sad', 'upset']

                        if emotion_key not in valid_emotions:
                            raise ValueError(f"잘못된 감정 키: {emotion_key}")

                        # 해당 행의 인덱스를 구함
                        mask = db['Data'] == user_text
                        if not mask.any():
                            raise ValueError(f"{user_text} 지역이 데이터에 존재하지 않습니다.")

                        # 인덱스 기반 업데이트
                        db.loc[mask, emotion_key] += 1

                        # 저장
                        db.to_csv('emotion_db.csv', index=False)
                    except FileNotFoundError:
                        raise FileNotFoundError("데이터를 불러올 수 없습니다.")
                    
            else:
                raise ValueError("지원하지 않는 파일 형식입니다. JPG 또는 PNG 파일만 업로드할 수 있습니다.")
            
        
            return render_template('index.html', image_url=filepath, result=result, user_text=user_text, emoji_mapping=load_emoji_mapping())
    return render_template('index.html', image_url=None, result=None, user_text=None, emoji_mapping=load_emoji_mapping())

if __name__ == '__main__':
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)