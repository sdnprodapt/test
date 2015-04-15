FROM cyan/juniper-base

RUN mkdir -p /bp2/log

WORKDIR /bp2/src/

EXPOSE 8080

ENV NBI_ea_port=8080
ENV NBI_juniper_port=8080
ENV SBI_rabbitmq_providerCount=1

CMD ["juniper", "--configpath", "/tmp", "--logfile", "/bp2/log/eajuniper.log"]
