#!/bin/bash


##########################################################
# The setup_ssh script does the following:
#
#  - Sets up key-based SSH login, and
#    installs the private keys, so
#    we can connect to servers.
#
#  - Configures git, and adds the
#    upstream repo as a remote
#
# (see https://docs.gitlab.com/ce/ci/ssh_keys/README.html)
#
# NOTE: It is assumed that non-docker
#       executors are already configured
#       (or don't need any configuration).
##########################################################


if [[ -f /.dockerenv ]]; then

  apt-get update -y                           || yum -y check-update                     || true;
  apt-get install -y git rsync openssh-client || yum install -y git rsync openssh-client || true;

  eval $(ssh-agent -s);
  mkdir -p $HOME/.ssh;

  echo "$SSH_PRIVATE_KEY_GIT" > $HOME/.ssh/id_git;

  if [[ "$CI_PROJECT_PATH" == "$UPSTREAM_PROJECT" ]]; then
    echo "$SSH_PRIVATE_KEY_DOC_DEPLOY"   > $HOME/.ssh/id_doc_deploy;
    echo "$SSH_PRIVATE_KEY_CONDA_DEPLOY" > $HOME/.ssh/id_conda_deploy;
  fi;

  chmod go-rwx $HOME/.ssh/id_*;

  ssh-add $HOME/.ssh/id_git;

  if [[ "$CI_PROJECT_PATH" == "$UPSTREAM_PROJECT" ]]; then
    ssh-add $HOME/.ssh/id_doc_deploy;
    ssh-add $HOME/.ssh/id_conda_deploy;
  fi

  echo "$SSH_SERVER_HOSTKEYS" > $HOME/.ssh/known_hosts;

  touch $HOME/.ssh/config;

  echo "Host ${UPSTREAM_URL##*@}"                    >> $HOME/.ssh/config;
  echo "    User ${UPSTREAM_URL%@*}"                 >> $HOME/.ssh/config;
  echo "    IdentityFile $HOME/.ssh/id_git"          >> $HOME/.ssh/config;

  echo "Host docdeploy"                              >> $HOME/.ssh/config;
  echo "    HostName ${DOC_HOST##*@}"                >> $HOME/.ssh/config;
  echo "    User ${DOC_HOST%@*}"                     >> $HOME/.ssh/config;
  echo "    IdentityFile $HOME/.ssh/id_doc_deploy"   >> $HOME/.ssh/config;

 echo "Host condadeploy"                            >> $HOME/.ssh/config;
 echo "    HostName ${CONDA_HOST##*@}"              >> $HOME/.ssh/config;
 echo "    User ${CONDA_HOST%@*}"                   >> $HOME/.ssh/config;
 echo "    IdentityFile $HOME/.ssh/id_conda_deploy" >> $HOME/.ssh/config;

  echo "Host *"                                      >> $HOME/.ssh/config;
  echo "    IdentitiesOnly yes"                      >> $HOME/.ssh/config;

  git config --global user.name  "Gitlab CI";
  git config --global user.email "gitlabci@localhost";

  if [[ `git remote -v` == *"upstream"* ]]; then
      git remote remove upstream;
  fi;
  git remote add upstream "$UPSTREAM_URL:$UPSTREAM_PROJECT";
fi
