FROM registry.fedoraproject.org/fedora-minimal:36
#FROM registry.access.redhat.com/ubi8/openjdk-17-runtime:1.16-2

RUN microdnf install -y \
    iputils \
    kubernetes-client \
    bind-utils \ 
    nmap-ncat     \            
    python3 python3-pip python3-kafka \
    shadow \
    curl bind-utils netcat openssl tar gzip less jq vim-minimal \
    gcc-c++ \
    make \
    librdkafka-devel \
    git \
&&  microdnf clean all



# # Clean up unnecessary packages
# RUN microdnf remove -y gcc-c++ make git \
#     && microdnf clean all

# Copy all custom scripts into a directory on the $PATH.
COPY scripts/* /usr/local/bin/



WORKDIR /home/

COPY *.py /home/


COPY       requirements.txt /home/

RUN        pip install -r requirements.txt


CMD ["/usr/local/bin/init.sh"]


