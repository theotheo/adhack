import cv2
import time
import pickle
import face_recognition
import numpy as np
import cv2
import uuid 
import pandas as pd 
import os
from recommendations import create_html
from face import face

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template("templates/result.html")
df = pd.read_csv('data/profiles.csv')
df['uid'] = df['uid'].astype('str')
df = df.set_index('uid')
print(df)
print(df.loc['144144243']['sex'])

class Camera():
    # Constructor...
    def __init__(self):
        w     = 640            # Frame width...
        h     = 480            # Frame hight...
        fps   = 20.0                    # Frames per second...
        resolution = (w, h)             # Frame size/resolution...
 
        self.cap = cv2.VideoCapture(0)  # Prepare the camera...
        print("Camera warming up ...")
        time.sleep(1)
        # Prepare Capture
        self.ret, self.frame = self.cap.read()
 
        # Prepare output window...
        self.winName = "Motion Indicator"
        cv2.namedWindow(self.winName, cv2.WINDOW_AUTOSIZE)
 
        # Read three images first...
        # self.prev_frame     = cv2.cvtColor(self.cap.read()[1],cv2.COLOR_RGB2GRAY)
        # self.current_frame  = cv2.cvtColor(self.cap.read()[1],cv2.COLOR_RGB2GRAY)
        # self.next_frame        = cv2.cvtColor(self.cap.read()[1],cv2.COLOR_RGB2GRAY)
 
        # Define the codec and create VideoWriter object
        # self.fourcc = cv2.VideoWriter_fourcc(*'H264')     # You also can use (*'XVID')
        # self.out = cv2.VideoWriter('output.avi',self.fourcc, fps, (w, h), True)


        with open('data/vk.pkl', 'rb') as f:
            uids_with_faces_encodings = pickle.load(f)
        self.uids = list(uids_with_faces_encodings.keys())
        print(self.uids)
        self.known_faces_encodings = list(uids_with_faces_encodings.values())

        # Initialize some variables
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True
        self.prev_fn = ''
    
    # Frame generation for Browser streaming wiht Flask...    
    def get_frame(self):
            
        fn = None
        self.frames = open("stream.jpg", 'wb+')
        self.ret, self.frame = self.cap.read()
# Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(self.frame, (0, 0), fx=0.25, fy=0.25)

        # Only process every other frame of video to save time
        if self.process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(small_frame)
            face_encodings = face_recognition.face_encodings(small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                # results = face_recognition.compare_faces(self.known_faces_encodings, face_encoding)
                face_distances = face_recognition.face_distance(self.known_faces_encodings, face_encoding)
                # print(face_distances)
                # print()
                
                # print(results)
                # import ipdb; ipdb.set_trace();
                if min(face_distances) < 0.5:
                    # uid = uids[results.index(True)]
                    uid = self.uids[np.argmin(face_distances)]
                    name = uid
                else:
                    name = uuid.uuid4().hex
                    self.uids.append(name)
                    self.known_faces_encodings.append(face_encoding)
                    # name = "Unknown"
                face_names.append(name)

        process_this_frame = not self.process_this_frame


        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            crop_face = self.frame[top:bottom, left:right]
            fn = 'data/new_faces/{}.png'.format(name)
            if not os.path.isfile(fn):
                cv2.imwrite(fn, crop_face)
                cv2.imwrite('static/{}.png'.format(name), crop_face)

            # Draw a box around the face
            cv2.rectangle(self.frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(self.frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(self.frame, str(name), (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        if self.ret:    # frame captures without errors...
            cv2.imwrite("stream.jpg", self.frame)    # Save image...

        with open('result.html', 'w') as f:

            result = pd.DataFrame()
            result['uid'] = face_names
            fns = []
            vks = []
            genders = []
            for uid in face_names:
                
                if uid in df.index:
                    print("&&&&&&&&&&&&&&&&")
                    kind = 'familiar'
                    fns.append('/static/{}.jpg'.format(uid))
                    vks.append('https://vk.com/id{}'.format(uid))
                    # import ipdb; ipdb.set_trace()
                    genders.append(df.loc[uid]['sex'])
                else:
                    print(self.prev_fn)
                    print(fn)
                    res = {}
                    if self.prev_fn != fn:
                        res = face(fn)
                        print(res)
                        if 'error' not in res:
                            try: 
                                res = res[0].get('faceAttributes')
                            except:
                                print(res)
                                res = {}
                            self.prev_fn = fn

                    kind = res.get('gender', 'None')
                    print(kind)
                    genders.append(kind)
                    fns.append('/static/{}.png'.format(uid))
                    vks.append(None)
                if uid == '144144243':
                    kind = 'friend'

                print(kind)
            if face_names:
                create_html(face_names[0], kind)
            else:
                create_html('0', 'empty')
            result['photo'] = fns
            result['vk'] = vks
            result['gender'] = genders
            # print(result)
            f.write(template.render({'x': result}))


        return self.frames.read()
        
            
    # def diffImg(self, tprev, tc, tnex):
    #     # Generate the 'difference' from the 3 captured images...
    #     Im1 = cv2.absdiff(tnex, tc)
    #     Im2 = cv2.absdiff(tc, tprev)
    #     return cv2.bitwise_and(Im1, Im2)
 
    # def captureVideo(self):
    #     # Read in a new frame...
    #     self.ret, self.frame = self.cap.read()
    #     # Image manipulations come here...
    #             # This line displays the image resulting from calculating the difference between
    #             # consecutive images...
    #     diffe = self.diffImg(self.prev_frame, self.current_frame, self.next_frame)
    #     cv2.imshow(self.winName,diffe)
        
    #     # Put images in the right order...
    #     self.prev_frame        = self.current_frame
    #     self.current_frame    = self.next_frame
    #     self.next_frame        = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)
    #     return()
 
    # def saveVideo(self):
    #     # Write the frame...
    #     self.out.write(self.frame)
    #     return()
 
    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.out.release()
        print("Camera disabled and all output windows closed...")
        return()
 
def main():
    # Create a camera instance...
    cam1 = Camera()
 
    while(True):
        # Display the resulting frames...
        cam1.captureVideo()    # Live stream of video on screen...
        cam1.saveVideo()       # Save video to file 'output.avi'...
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    return()
 
if __name__=='__main__':
    main()