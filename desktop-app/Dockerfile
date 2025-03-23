FROM ubuntu:22.04
ENV TZ=Europe/Paris DEBIAN_FRONTEND=noninteractive

# Install GUI libraries and X11 utilities
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    python3 python3-pip python3-dev python3-tk \
    libjpeg-dev zlib1g-dev libfreetype6-dev \
    tcl-dev tk-dev xvfb x11-xserver-utils \
    xdotool x11-utils x11vnc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    PyQt5 PyQtWebEngine Pillow

# Set VNC password
RUN mkdir -p /root/.vnc && \
    echo "42" | openssl passwd -1 -stdin > /root/.vnc/passwd && \
    chmod 600 /root/.vnc/passwd

WORKDIR /app
COPY . .

RUN ls -l /app

# Set the display environment variable
ENV DISPLAY=:99

# Run the Xvfb display server and your Tkinter application
CMD ["sh", "-c", "Xvfb :99 -screen 0 1400x900x24 & sleep 3 && x11vnc -forever -usepw -create -display :99 & python3 src/main_window.py"]