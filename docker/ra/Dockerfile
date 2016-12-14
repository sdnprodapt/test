FROM cyan/rajuniper-base

RUN mkdir -p /bp2/log

WORKDIR /bp2/src/

EXPOSE 8080

ENV NBI_ra_port=8080
ENV NBI_ra_publish=True
ENV NBI_rajuniper_type=http
ENV NBI_rajuniper_internal=True
ENV NBI_rajuniper_port=8080
ENV NBI_rajuniper_publish=True
ENV SBIS=bpocore,git-ssh,kafka
ENV BP2HOOK_heartbeat=/bin/true \
    BP2HOOK_peer-status=bp2-peer-depart \
    BP2HOOK_peer-update=/bin/true

RUN ln -s /usr/local/bin/rasdk-southbound-update /usr/local/bin/southbound-update

ENV SBI_git-ssh_southbound-update=bpocore-sb-update

CMD ["rajuniper", "--no-clustering", "--declare-rp", "--configpath", "/tmp", "--logfile", "/bp2/log/rajuniper.log"]
