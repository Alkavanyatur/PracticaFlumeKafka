# README


Este ejercicio forma parte de la práctica de Flume-Kafka del bloque 3



### Parte 1

Fichero: practica_flume_kafka.conf

Lo primero que hacemos es crear un directorio donde vamos a escribir el archivo.

```
sudo mkdir /opt/flumetest
```

Copiamos el archivo adjunto, en caso de no tenerlo creamos el archivo vacío.

```
sudo nano practica_flume_kafka.conf
```

Y copiamos la siguiente configuración (o en su defecto el archivo):

```
#Configuracion global
agente.sources = r1
agente.channels = c1
agente.sinks=k1
#Configuracion de la fuente
agente.sources.r1.type = org.apache.flume.source.twitter.TwitterSource
agente.sources.r1.channels = c1
agente.sources.r1.consumerKey = 
agente.sources.r1.consumerSecret = 
agente.sources.r1.accessToken = 
agente.sources.r1.accessTokenSecret = 
agente.sources.r1.maxBatchSize = 10
agente.sources.r1.maxBatchDurationMillis = 200
#Configuracion del canal
agente.channels.c1.type=memory
#Configuracion del destino
agente.sinks.k1.channel = c1
agente.sinks.k1.type = org.apache.flume.sink.kafka.KafkaSink
agente.sinks.k1.kafka.topic = tweets_name
agente.sinks.k1.kafka.bootstrap.servers = localhost:9092
agente.sinks.k1.kafka.flumeBatchSize = 20
agente.sinks.k1.kafka.producer.acks = 1
agente.sinks.k1.kafka.producer.linger.ms = 1
agente.sinks.k1.kafka.producer.compression.type = snappy
```

Guardamos el archivo y lo cerramos. Verificamos que ha quedado bien escribo con cat /opt/flumetest/practica_flume_kafka.conf y arrancamos flume de la siguiente manera:

```
flume-ng agent --conf ./conf --conf-file /opt/flumetest/practica_flume_kafka.conf  --name flumetest -Dflume.root.logger=INFO,console
```

En la carpeta /usr/local ejecutamos para arrancar kafka

```
bin/kafka-server-start.sh config/server.properties
```


### Parte 2

Lanzamos el siguiente comando dentro de /usr/local/kafka para crear el topic

```
bin/kafka-console-producer.sh --broker-list localhost:9092 --topic tweets_name
```

Lo probamos de la siguiente manera, arrancamos un consumer

```
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --property print.key=true --topic tweets_name  --new-consumer --consumer.config config/consumer.properties
```

Y volvemos a la ventana del producer para escribir, cualquier mensaje nos vale. Si lo hemos hecho bien, veremos en la ventana del consumer el mensaje.



### Parte 3

Para este punto hemos instalado una librería de python:

```
pip install tweepy
```

Después de esto hemos iniciado python y copiado el siguiente código:

También podemos crear un archivo .py y lanzarlo mediante python <nombre_del_archivo.py> previamente cambiamos los permisos del archivo con chmod para hacerlo ejecutable.


```
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import SimpleProducer, KafkaClient
import json

access_token = ""
access_token_secret =  ""
consumer_key =  ""
consumer_secret =  ""

class StdOutListener(StreamListener):
    def on_data(self, data):
        producer.send_messages("tweets_name", data.encode('utf-8'))
		all_data = json.loads(data)
		tweet = all_data["text"]
        print (tweet)
        return True
    def on_error(self, status):
        print (status)

kafka = KafkaClient("localhost:9092")
producer = SimpleProducer(kafka)
l = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, l)
stream.filter(track="errejon")
```

Obtenido de aquí:

https://www.bmc.com/blogs/working-streaming-twitter-data-using-kafka/


Ejercicios:

### A: 		Extraemos los tweets (el texto) de esta manera:

		producer.send_messages("tweets_name", data.encode('utf-8'))
		all_data = json.loads(data)
		if "Text" in all_data:
			tweet = all_data["text"]
			print (tweet)
			return True
		else:
			print("User vacio")
			return True
		def on_error(self, status):
			print (status)	
		
### B:
### C:
### D:		Obtenemos los autores de esta manera:

		def on_data(self, data):
		producer.send_messages("tweets_name", data.encode('utf-8'))
		all_data = json.loads(data)
		if "user" in all_data:
			tweet = all_data["user"]["screen_name"]
				print (tweet)
				return True
		else:
			print("User vacio")
			return True
		def on_error(self, status):
			print (status)


			
### ADICIONALMENTE  He tratado de hacerlo con pyspark

Instalamos spark

```
sudo apt-get install spark
```

Instalamos pyspark, utilizando el --no-cache-dir ya que nos daba problemas de memoria.

```
pip --no-cache-dir install pyspark
```

Y utilizando este código.

```
import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 pyspark-shell'

import os  
from pyspark import SparkContext  
from pyspark.streaming import StreamingContext  
from pyspark.streaming.kafka import KafkaUtils  
import json  

def createContext():  
    sc = SparkContext(appName="pySparkStreamingKafka")
    sc.setLogLevel("WARN")
    ssc = StreamingContext(sc, 5)

    # Definir el consmidor de kafka indicando el servidor de zookeeper , el group id  y el topic
    kafkaStream = KafkaUtils.createStream(ssc, 'localhost:9092', 'spark-streaming', {'tweets_name':1})

    
    # Extraer los tweets
    parsed = kafkaStream.map(lambda v: json.loads(v[1]))

    # Se cuentan los tweets en un bach
    count_this_batch = kafkaStream.count().map(lambda x:('Tweets en el batch: %s' % x))

    # Se cuentan por una ventana de tiempo
    count_windowed = kafkaStream.countByWindow(60,5).map(lambda x:('Tweets totales (agrupados en un minuto): %s' % x))

    # Obtenemos los autores
    authors_dstream = parsed.map(lambda tweet: tweet['user']['screen_name'])

    # 
    count_values_this_batch = authors_dstream.countByValue()\
                                .transform(lambda rdd:rdd\
                                  .sortBy(lambda x:-x[1]))\
                              .map(lambda x:"Autores contados en el batch:\tValue %s\tCount %s" % (x[0],x[1]))

   
    count_values_windowed = authors_dstream.countByValueAndWindow(60,5)\
                                .transform(lambda rdd:rdd\
                                  .sortBy(lambda x:-x[1]))\
                            .map(lambda x:"Autores contados por un minuto:\tValue %s\tCount %s" % (x[0],x[1]))

    count_this_batch.union(count_windowed).pprint()

    # Se muestra el resultado por pantalla
    count_values_this_batch.pprint(5)
    count_values_windowed.pprint(5)

    return ssc
# Se debe tener cuidado con el checkpoint ya que si existe un error puede provocar inconsistencia en futuras ejecuciones
ssc = StreamingContext.getOrCreate('/tmp/checkpoint_v01',lambda: createContext())  
ssc.start()  
ssc.awaitTermination() 
```

Obtenido de aquí:

https://github.com/alejgamez/sparkStreaming/blob/20d4b694cdfd4430713d9538b3964ab80fd8e402/twitter-kafka.py		


Ejecutandolo de la siguiente manera:

```
/usr/local/bin/spark-submit --jars spark-streaming-kafka-0-8_2.11-2.1.1.jar testSpark.py
```

Que da como resultado el error:

```
2018-04-01 21:44:33 WARN  Utils:66 - Your hostname, sbd-VirtualBox resolves to a loopback address: 127.0.1.1; using 10.0.2.15 instead (on interface enp0s3)
2018-04-01 21:44:33 WARN  Utils:66 - Set SPARK_LOCAL_IP if you need to bind to another address
2018-04-01 21:44:34 WARN  NativeCodeLoader:62 - Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
2018-04-01 21:44:35 WARN  Checkpoint:66 - Checkpoint directory /home/sbd/tmp/check does not exist
2018-04-01 21:44:35 INFO  SparkContext:54 - Running Spark version 2.3.0
2018-04-01 21:44:35 INFO  SparkContext:54 - Submitted application: tweets_name
2018-04-01 21:44:36 INFO  SecurityManager:54 - Changing view acls to: sbd
2018-04-01 21:44:36 INFO  SecurityManager:54 - Changing modify acls to: sbd
2018-04-01 21:44:36 INFO  SecurityManager:54 - Changing view acls groups to: 
2018-04-01 21:44:36 INFO  SecurityManager:54 - Changing modify acls groups to: 
2018-04-01 21:44:36 INFO  SecurityManager:54 - SecurityManager: authentication disabled; ui acls disabled; users  with view permissions: Set(sbd); groups with view permissions: Set(); users  with modify permissions: Set(sbd); groups with modify permissions: Set()
2018-04-01 21:44:36 INFO  Utils:54 - Successfully started service 'sparkDriver' on port 38913.
2018-04-01 21:44:36 INFO  SparkEnv:54 - Registering MapOutputTracker
2018-04-01 21:44:36 INFO  SparkEnv:54 - Registering BlockManagerMaster
2018-04-01 21:44:36 INFO  BlockManagerMasterEndpoint:54 - Using org.apache.spark.storage.DefaultTopologyMapper for getting topology information
2018-04-01 21:44:36 INFO  BlockManagerMasterEndpoint:54 - BlockManagerMasterEndpoint up
2018-04-01 21:44:36 INFO  DiskBlockManager:54 - Created local directory at /tmp/blockmgr-be48e634-c4fe-41d9-88f9-075bc44fde2e
2018-04-01 21:44:36 INFO  MemoryStore:54 - MemoryStore started with capacity 413.9 MB
2018-04-01 21:44:36 INFO  SparkEnv:54 - Registering OutputCommitCoordinator
2018-04-01 21:44:37 INFO  log:192 - Logging initialized @4594ms
2018-04-01 21:44:37 INFO  Server:346 - jetty-9.3.z-SNAPSHOT
2018-04-01 21:44:37 INFO  Server:414 - Started @4904ms
2018-04-01 21:44:37 INFO  AbstractConnector:278 - Started ServerConnector@718e32b7{HTTP/1.1,[http/1.1]}{0.0.0.0:4040}
2018-04-01 21:44:37 INFO  Utils:54 - Successfully started service 'SparkUI' on port 4040.
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@53917f3a{/jobs,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@466e7e76{/jobs/json,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@32d89dff{/jobs/job,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@6d0215bf{/jobs/job/json,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@58aa5ba7{/stages,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@2eeb1228{/stages/json,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@19a99243{/stages/stage,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@188aeec5{/stages/stage/json,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@4d645c1d{/stages/pool,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@773c4476{/stages/pool/json,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@2f39b4cd{/storage,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@608a9b29{/storage/json,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@fe1b791{/storage/rdd,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@1a6b5def{/storage/rdd/json,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@78960db3{/environment,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@4c71925b{/environment/json,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@4e2ef97b{/executors,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@e6a5174{/executors/json,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@46d92e9f{/executors/threadDump,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@6fa9f55{/executors/threadDump/json,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@3f265bd0{/static,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@58b7e228{/,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@f563984{/api,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@3d489c2e{/jobs/job/kill,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@3dd60ac9{/stages/stage/kill,null,AVAILABLE,@Spark}
2018-04-01 21:44:37 INFO  SparkUI:54 - Bound SparkUI to 0.0.0.0, and started at http://10.0.2.15:4040
2018-04-01 21:44:37 INFO  SparkContext:54 - Added JAR file:///opt/flumetest/spark-streaming-kafka-0-8_2.11-2.1.1.jar at spark://10.0.2.15:38913/jars/spark-streaming-kafka-0-8_2.11-2.1.1.jar with timestamp 1522611877937
2018-04-01 21:44:37 INFO  SparkContext:54 - Added file file:/opt/flumetest/testSpark.py at file:/opt/flumetest/testSpark.py with timestamp 1522611877950
2018-04-01 21:44:37 INFO  Utils:54 - Copying /opt/flumetest/testSpark.py to /tmp/spark-e2a0fbef-4dd1-4cd5-8c3c-6ce0d42948af/userFiles-a68a4e79-1841-4953-8117-d8cfc881f27a/testSpark.py
2018-04-01 21:44:38 INFO  Executor:54 - Starting executor ID driver on host localhost
2018-04-01 21:44:38 INFO  Utils:54 - Successfully started service 'org.apache.spark.network.netty.NettyBlockTransferService' on port 38993.
2018-04-01 21:44:38 INFO  NettyBlockTransferService:54 - Server created on 10.0.2.15:38993
2018-04-01 21:44:38 INFO  BlockManager:54 - Using org.apache.spark.storage.RandomBlockReplicationPolicy for block replication policy
2018-04-01 21:44:38 INFO  BlockManagerMaster:54 - Registering BlockManager BlockManagerId(driver, 10.0.2.15, 38993, None)
2018-04-01 21:44:38 INFO  BlockManagerMasterEndpoint:54 - Registering block manager 10.0.2.15:38993 with 413.9 MB RAM, BlockManagerId(driver, 10.0.2.15, 38993, None)
2018-04-01 21:44:38 INFO  BlockManagerMaster:54 - Registered BlockManager BlockManagerId(driver, 10.0.2.15, 38993, None)
2018-04-01 21:44:38 INFO  BlockManager:54 - Initialized BlockManager: BlockManagerId(driver, 10.0.2.15, 38993, None)
2018-04-01 21:44:38 INFO  ContextHandler:781 - Started o.s.j.s.ServletContextHandler@1e45fdfb{/metrics/json,null,AVAILABLE,@Spark}
ERROR:root:Exception while sending command.
Traceback (most recent call last):
  File "/usr/local/lib/python2.7/dist-packages/pyspark/python/lib/py4j-0.10.6-src.zip/py4j/java_gateway.py", line 908, in send_command
    response = connection.send_command(command)
  File "/usr/local/lib/python2.7/dist-packages/pyspark/python/lib/py4j-0.10.6-src.zip/py4j/java_gateway.py", line 1067, in send_command
    "Error while receiving", e, proto.ERROR_ON_RECEIVE)
Py4JNetworkError: Error while receiving
Traceback (most recent call last):
  File "/opt/flumetest/testSpark.py", line 50, in <module>
    ssc = StreamingContext.getOrCreate("/home/sbd/tmp/check",lambda: createContext())  
  File "/usr/local/lib/python2.7/dist-packages/pyspark/python/lib/pyspark.zip/pyspark/streaming/context.py", line 121, in getOrCreate
  File "/opt/flumetest/testSpark.py", line 50, in <lambda>
    ssc = StreamingContext.getOrCreate("/home/sbd/tmp/check",lambda: createContext())  
  File "/opt/flumetest/testSpark.py", line 14, in createContext
    kafkaStream = KafkaUtils.createStream(ssc, 'localhost:9092', 'kafka', {'tweets_name':1})
  File "/usr/local/lib/python2.7/dist-packages/pyspark/python/lib/pyspark.zip/pyspark/streaming/kafka.py", line 79, in createStream
  File "/usr/local/lib/python2.7/dist-packages/pyspark/python/lib/py4j-0.10.6-src.zip/py4j/java_gateway.py", line 1160, in __call__
  File "/usr/local/lib/python2.7/dist-packages/pyspark/python/lib/py4j-0.10.6-src.zip/py4j/protocol.py", line 328, in get_return_value
py4j.protocol.Py4JError: An error occurred while calling o28.createStream
Exception in thread "Thread-6" java.lang.NoClassDefFoundError: kafka/common/TopicAndPartition
    at java.lang.Class.getDeclaredMethods0(Native Method)
    at java.lang.Class.privateGetDeclaredMethods(Class.java:2701)
    at java.lang.Class.privateGetPublicMethods(Class.java:2902)
    at java.lang.Class.getMethods(Class.java:1615)
    at py4j.reflection.ReflectionEngine.getMethodsByNameAndLength(ReflectionEngine.java:345)
    at py4j.reflection.ReflectionEngine.getMethod(ReflectionEngine.java:305)
    at py4j.reflection.ReflectionEngine.getMethod(ReflectionEngine.java:326)
    at py4j.Gateway.invoke(Gateway.java:274)
    at py4j.commands.AbstractCommand.invokeMethod(AbstractCommand.java:132)
    at py4j.commands.CallCommand.execute(CallCommand.java:79)
    at py4j.GatewayConnection.run(GatewayConnection.java:214)
    at java.lang.Thread.run(Thread.java:748)
Caused by: java.lang.ClassNotFoundException: kafka.common.TopicAndPartition
    at java.net.URLClassLoader.findClass(URLClassLoader.java:381)
    at java.lang.ClassLoader.loadClass(ClassLoader.java:424)
    at java.lang.ClassLoader.loadClass(ClassLoader.java:357)
    ... 12 more
```


### Fuentes:

https://stackoverflow.com/questions/29466663/memory-error-while-using-pip-install-matplotlib#_=_

https://dzone.com/articles/how-do-data-ingestion-with-apache-flume-sending-ev

http://flume.apache.org/FlumeUserGuide.html#kafka-sink

http://www.bmc.com/blogs/working-streaming-twitter-data-using-kafka/

https://gist.github.com/rmoff/eadf82da8a0cd506c6c4a19ebd18037e
