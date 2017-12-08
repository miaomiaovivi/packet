#!/bin/bash
echo "Syncing your project with gcloud. "
echo "Make sure to add your public key into VM's ~/.ssh/authorized_keys first."
CLIENT="~ client IP ~"
SCHEDULER="~ scheduler IP ~"
STANDBY="~ standby IP1 ~"
ACTIVE="~ Active IP ~"
WORKDIR=$PWD
USERNAME="~your gcloud login username~"

rsync -a $WORKDIR $USERNAME@${STANDBY}:/home/$USERNAME/project5
rsync -a $WORKDIR $USERNAME@${ACTIVE}:/home/$USERNAME/project5
rsync -a $WORKDIR $USERNAME@${CLIENT}:/home/$USERNAME/project5
rsync -a $WORKDIR $USERNAME@${SCHEDULER}:/home/$USERNAME/project5
