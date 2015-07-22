FROM cyan/juniper-base

RUN mkdir -p /bp2/log

WORKDIR /bp2/src/

EXPOSE 8080

ENV NBI_ea_port=8080
ENV NBI_ea_publish=True
ENV NBI_eajuniper_port=8080
ENV NBI_eajuniper_publish=True
ENV SBIS=rabbitmq,bpocore,git-ssh

RUN ln -s /bp2/hooks/bpocore-sb-update /usr/local/bin/bpocore-sb-update

ENV SBI_bpocore_southbound-update=bpocore-sb-update
ENV SBI_git-ssh_southbound-update=bpocore-sb-update

CMD ["juniper", "--configpath", "/tmp", "--logfile", "/bp2/log/eajuniper.log"]