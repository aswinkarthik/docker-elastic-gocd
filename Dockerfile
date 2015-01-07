FROM centos
COPY ./bin/ /data/ 
RUN mkdir -p /etc/default/
RUN mkdir -p /var/lib/go-agent
RUN yum install -y java-1.7.0-openjdk.x86_64
RUN yum localinstall -y /data/*.rpm
RUN cat /etc/default/go-agent
COPY config/go-agent /etc/default/go-agent
RUN cat /etc/default/go-agent
RUN mkdir -p /var/log/go-agent
ENTRYPOINT /etc/init.d/go-agent restart && /bin/bash