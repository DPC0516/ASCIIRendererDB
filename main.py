import discord
from renderer import Renderer
import os
import cv2

PATH_FRAMES = "frames/"
PATH_SOURCE_VIDEO = "source_video/"

SOURCE_VIDEO_NAME = ""

IS_CONVERTED_TO_FRAME = False

IS_IN_PROGRESS = False

FRAMES = []
IS_FRAME_RENDERED = False
FRAME_EXCEPT_TIME = 4

client = discord.Client()

msg = None


def get_clip_frames():
    file_list = os.listdir(PATH_FRAMES)
    return len(file_list)


@client.event
async def on_ready():
    print("ready")


@client.event
async def on_message(message):
    global IS_FRAME_RENDERED
    global FRAMES
    global FRAME_EXCEPT_TIME
    global IS_CONVERTED_TO_FRAME
    global SOURCE_VIDEO_NAME
    global msg
    global IS_IN_PROGRESS

    if not IS_IN_PROGRESS:
        if message.content.startswith("!set_source_video_name"):
            back_up = SOURCE_VIDEO_NAME
            try:
                SOURCE_VIDEO_NAME = message.content.split()[1]
                await message.channel.send("source video name set to " + SOURCE_VIDEO_NAME)
            except Exception:
                SOURCE_VIDEO_NAME = back_up
                await message.channel.send("source video name set failure")
            IS_CONVERTED_TO_FRAME = back_up == SOURCE_VIDEO_NAME

        if message.content.startswith("!convert_to_frame"):
            IS_IN_PROGRESS = True
            try:
                video_object = cv2.VideoCapture(PATH_SOURCE_VIDEO + SOURCE_VIDEO_NAME)

                await message.channel.send("deleting frames")
                os.rmdir(PATH_FRAMES)
                os.mkdir(PATH_FRAMES)

                count = 0

                while True:
                    success, image = video_object.read()
                    if success:
                        cv2.imwrite(PATH_FRAMES + "frame" + str(count) + ".jpg", image)

                        count += 1

                        if count % 100 == 0:
                            await message.channel.send("converting frame " + str(count))
                    else:
                        break
                IS_CONVERTED_TO_FRAME = True
            except Exception:
                await message.channel.send("unable to open source video")
            IS_IN_PROGRESS = False

        if message.content.startswith("!play"):
            IS_IN_PROGRESS = True
            if not IS_CONVERTED_TO_FRAME:
                await message.channel.send("source video has not been converted to frames")
            else:
                if not IS_FRAME_RENDERED:
                    FRAMES.clear()

                    msg = await message.channel.send("rendering frames")

                    for i in range(0, int((get_clip_frames() / FRAME_EXCEPT_TIME) + 1)):
                        FRAMES.append(Renderer.runner(PATH_FRAMES + "frame" + str(i * FRAME_EXCEPT_TIME) + ".jpg"))
                        if i % 100 == 0:
                            print("rendering " + str(i) + "/" +
                                  str(int(get_clip_frames() / FRAME_EXCEPT_TIME)))
                            await msg.edit(content="rendering " + str(i) + "/" +
                                                       str(int(get_clip_frames() / FRAME_EXCEPT_TIME)))
                    await message.channel.send("rendering finished")
                    IS_FRAME_RENDERED = True

                for i in range(0, len(FRAMES) - 1):
                    await message.channel.send(".\n" + FRAMES[int(i)])
            IS_IN_PROGRESS = False


client.run('ODY0Mzc0ODE0NDg3NzQwNDE4.YO0hxw.oTkgiDwMd4h2PyehCMOdkN6dKkY')
