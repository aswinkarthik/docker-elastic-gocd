FROM centos
COPY ./bin/ /data/ 
RUN mkdir -p /etc/default/
RUN mkdir -p /var/lib/go-agent
RUN yum localinstall -y /data/java*.rpm
RUN yum localinstall -y /data/go*.rpm
COPY bin/go-agent /etc/default/go-agent
RUN cat /etc/default/go-agent
RUN mkdir -p /var/log/go-agent
ENTRYPOINT /etc/init.d/go-agent start && tail -f /var/log/go-agent/*