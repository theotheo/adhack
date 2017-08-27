from flask import Flask, render_template, Response, send_file, send_from_directory
 
# emulated camera
from face_camera import Camera
 
# If you are using a webcam -> no need for changes
# if you are using the Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera
 
app = Flask(__name__, static_folder='static')
 
 
@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')
 
 
def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + bytearray(frame) + b'\r\n')
 
 
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
 
@app.route('/result.html')
def show_result():
    return send_file('result.html')


@app.route('/static/MDB-Free/recommendations.html')
def show_recs():
    print()
    # return send_file('/static/MDB-Free/recommendations.html')
    return send_from_directory(app.static_folder, 'MDB-Free/recommendations.html')

# @app.route('/<path:path>')
# def static_file(path):
#     return app.send_static_file(path)

@app.route('/<path:filename>')
def send_new_faces(filename):
    print(filename)
    return send_from_directory(app.static_folder, filename)

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)