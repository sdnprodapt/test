FROM cyan/rajuniper-base

RUN mkdir -p /bp2/log

# lxml dependency
RUN apt-get update -y -q
RUN apt-get install -y -q libxslt-dev libxml2-dev libffi-dev libssl-dev openjdk-7-jre-headless

WORKDIR /bp2/src/

EXPOSE 8080

ENV RASDK_SETTINGS_MODULE=rajuniper.settings \
    NBI_ra_port=8080 \
    NBI_ra_publish=True \
    NBI_rajuniper_port=8080 \
    NBI_rajuniper_publish=True \
    SBIS=kafka,statsd,bpocore,git-ssh \
    BP2HOOK_heartbeat=/bin/true \
    BP2HOOK_peer-status=bp2-peer-depart \
    BP2HOOK_peer-update=/bin/true \
    BP2HOOK_southbound-update=rasdk-southbound-update

RUN ssh-keygen -t rsa -f /root/.ssh/id_rsa -q -N "" && \
    git config --global user.name rajuniper && \
    git config --global user.email rajuniper@ciena.com

CMD ["rajuniper", "--configpath", "/dev/shm", "--logfile", "/bp2/log/rajuniper.log", "--kafka"]
