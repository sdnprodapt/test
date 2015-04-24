FROM cyan/juniper-base

RUN mkdir -p /bp2/log

WORKDIR /bp2/src/

EXPOSE 8080

ENV NBI_ea_port=8080
ENV NBI_ea_publish=True
ENV NBI_juniper_port=8080
ENV NBI_juniper_publish=True
ENV SBIS=rabbitmq

CMD ["juniper", "--configpath", "/tmp", "--logfile", "/bp2/log/eajuniper.log"]
