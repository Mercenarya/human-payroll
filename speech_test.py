import speech_recognition as sr

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Nói gì đó...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio, language="en-US")
        print("Bạn đã nói: " + text)
    except sr.UnknownValueError:
        print("Không nhận diện được giọng nói.")
    except sr.RequestError:
        print("Không thể kết nối đến dịch vụ nhận diện giọng nói.")

if __name__ == "__main__":
    recognize_speech()