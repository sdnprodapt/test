FROM cyan/rajuniper-base

RUN mkdir -p /bp2/log

WORKDIR /bp2/src/

EXPOSE 8080

ENV NBI_ra_port=8080
ENV NBI_ra_publish=True
ENV NBI_rajuniper_port=8080
ENV NBI_rajuniper_publish=True
ENV SBIS=rabbitmq,bpocore,git-ssh,kafka

RUN ln -s /bp2/hooks/bpocore-sb-update /usr/local/bin/bpocore-sb-update

ENV SBI_bpocore_southbound-update=bpocore-sb-update
ENV SBI_git-ssh_southbound-update=bpocore-sb-update
ENV SBI_kafka_southbound-update=bpocore-sb-update

CMD ["rajuniper", "--no-clustering", "--declare-rp", "--configpath", "/tmp", "--logfile", "/bp2/log/rajuniper.log"]
