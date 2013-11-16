#!/bin/sh

DB_URL=$CLEARDB_DATABASE_URL
# extract the protocol
proto=`echo $DB_URL | grep '://' | sed -e 's,^\(.*://\).*,\1,g'`

# remove the protocol
url=`echo $DB_URL | sed -e s,$proto,,g`

# extract the user and password (if any)
userpass=`echo $url | grep @ | cut -d @ -f 1`
pass=`echo $userpass | grep : | cut -d : -f 2`
if [ -n "$pass" ]; then
  user=`echo $userpass | grep : | cut -d : -f 1`
else
  user=$userpass
fi

# extract the host -- updated
hostport=`echo $url | sed -e s,$userpass@,,g | cut -d / -f 1`
port=`echo $hostport | grep : | cut -d : -f 2`
if [ -n "$port" ]; then
  host=`echo $hostport | grep : | cut -d : -f 1`
else
  host=$hostport
fi

# extract the path (if any)
path="`echo $url | grep / | cut -d / -f 2-`"

# extract the dbname from path
db="`echo $path | grep ? | cut -d ? -f 1`"
query="`echo $path | grep ? | cut -d ? -f 2-`"

debug=0
if [ "$debug" == 1 ]; then
  echo "url: $url"
  echo "  proto: $proto"
  echo "  user: $user"
  echo "  pass: $pass"
  echo "  hostport: $hostport"
  echo "  path: $path"
  echo "  query: $query"
  echo "  db: $db"
fi

JAVACMD=`which java`
BASEDIR=`pwd`/target
if [ -z "$REPO" ]; then
  REPO="$BASEDIR"/repo
fi

CLASSPATH="$BASEDIR"/etc
for jar in `find "$REPO" -name *.jar`; do
  CLASSPATH=$CLASSPATH:$jar
done

CMD=`which java`

# Get from heroku
PORT=${PORT:-61618}

cat > "$BASEDIR/classes/conf/user.properties" << EOF
metc.ws.host=localhost
metc.ws.port=9009
metc.jms.broker.url=tcp://\${metc.ws.host}:$PORT?wireFormat.maxInactivityDurationInitalDelay=30000
metc.jdbc.user=$user
metc.jdbc.password=$pass
metc.jdbc.url=jdbc:mysql://$hostport/$db?logSlowQueries=true&$query
EOF

CMD="$CMD -classpath $CLASSPATH"
# This argument have to be set before main class
CMD="$CMD -Dorg.marketcetera.appDir=$BASEDIR/classes" 
CMD="$CMD org.marketcetera.ors.OrderRoutingSystem" 
CMD="$CMD $@"
[ "$debug" == 1 ] && echo $CMD
exec $CMD

