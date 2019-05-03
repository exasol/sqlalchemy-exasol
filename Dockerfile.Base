# parent image
FROM python:3.6-slim

RUN apt-get update && apt-get install -y \
      locales \
      g++ \
      python3-dev \
      unixodbc \
      unixodbc-dev \
      libboost-date-time-dev \
      libboost-locale-dev \
      libboost-system-dev \
      iputils-ping \
      vim \
      git



RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8 

CMD ["bash"]
