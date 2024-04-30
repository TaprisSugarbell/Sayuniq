FROM python:3.11-alpine
ARG HOSTDOCKERGID
ARG USER_GID
ARG USER_UID
ARG USERNAME=sayucode

RUN apk add --no-cache \
    git \
    zsh \
    make \
    btop \
    curl \
    bash \
    sudo \
    ffmpeg \
    shadow \
    ncurses \
    github-cli \
    docker-cli \
    docker-cli-compose \
    docker-cli-buildx \
    docker-zsh-completion \
    zsh-syntax-highlighting

RUN addgroup -g $HOSTDOCKERGID host-docker
RUN addgroup -g ${USER_GID:-101} -S $USERNAME \
 && adduser -S -D -u ${USER_UID:-101} -G $USERNAME -s /bin/zsh -g $USERNAME -g host-docker $USERNAME
RUN echo $USERNAME 'ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN mkdir -p $HOME/.config && chown $USERNAME:$USERNAME -R $HOME/.config

USER $USERNAME

RUN git clone https://github.com/NachABR/dotfiles.git ~/dotfiles; \
    chmod +wx ~/dotfiles/install.sh; \
    bash ~/dotfiles/install.sh --overwrite --no-interactive; \
    rm -rf ~/dotfiles
RUN echo -e -n '\nexport PATH="$HOME/.local/bin:$PATH"' >> $HOME/.zshrc; \
    echo -e -n '\nalias docker="sudo docker"' >> $HOME/.zshrc
RUN curl -sSL https://install.python-poetry.org | python3 -
CMD ["sleep", "infinity"]