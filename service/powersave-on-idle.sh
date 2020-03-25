#!/bin/sh

# idle.py used as a system service.

if [ "$#" -eq 1 ] && stat "$1" >/dev/null 2>&1; then
  source "$1"
else
  echo >&2 "FATAL: powersave-on-idle.conf needs to be provided!"
  exit 1
fi

CURRENT_PATH=$(dirname "$0")
export PYTHONPATH=/usr/local/lib/python

INTERFACE_ARGS=$(echo "$INTERFACES" |sed -e 's/\([0-9a-z]\+\)/-i \1/g')
BLOCKDEVS_ARGS=$(echo "$BLOCKDEVS"  |sed -e 's/\([0-9a-z]\+\)/-b \1/g')

while true; do
  echo "Waiting for rates on interfaces \"$INTERFACES\" to be less then ${THRESHOLD_NET} B/s and on block devices" \
       "\"${BLOCKDEVS}\" to be less then ${THRESHOLD_BLOCK} B/s for ${WINDOW} seconds."

  if "${CURRENT_PATH}/idle.py" ${INTERFACE_ARGS} ${BLOCKDEVS_ARGS} -t ${THRESHOLD_NET} -r ${THRESHOLD_BLOCK} -w ${WINDOW}; then
    echo "Going to save power, rates were below their thresholds for ${WINDOW} seconds."
    eval $POWERSAVE_CMD
  else
    echo >&2 "Error executing ${CURRENT_PATH}/idle.py!"
    exit 1
  fi
done
