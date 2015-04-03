FROM cyan/juniper-base

WORKDIR /bp2/src/

EXPOSE 8080

ENV NBI_ea_port=8080
ENV NBI_juniper_port=8080
ENV SBI_rabbitmq_providerCount=1
ENV SBI_rabbitmq_southbound-update=juniper-bp2-southbound-update

CMD ["juniper", "--config", "/tmp"]
