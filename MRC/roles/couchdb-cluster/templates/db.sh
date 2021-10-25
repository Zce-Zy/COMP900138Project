curl -X POST -H "Content-Type: application/json" http://admin:9988@45.113.233.239:5984/_cluster_setup -d '{"action": "enable_cluster", "bind_address":"0.0.0.0", "username": "admin", "password":"9988", "port": 5984, "node_count": "3", "remote_node": "45.113.233.215", "remote_current_user": "admin", "remote_current_password": "9988" }'
curl -X POST -H "Content-Type: application/json" http://admin:9988@45.113.233.239:5984/_cluster_setup -d '{"action": "add_node", "host":"45.113.233.215", "port": 5984, "username": "admin", "password":"9988"}'
curl -X POST -H "Content-Type: application/json" http://admin:9988@45.113.233.239:5984/_cluster_setup -d '{"action": "finish_cluster"}'
curl -X POST -H "Content-Type: application/json" http://admin:9988@45.113.233.239:5984/_cluster_setup -d '{"action": "enable_cluster", "bind_address":"0.0.0.0", "username": "admin", "password":"9988", "port": 5984, "remote_node": "45.113.234.122", "remote_current_user": "admin", "remote_current_password": "9988" }'
curl -X POST -H "Content-Type: application/json" http://admin:9988@45.113.233.239:5984/_cluster_setup -d '{"action": "add_node", "host":"45.113.234.122", "port": 5984, "username": "admin", "password":"9988"}'
curl -X POST -H "Content-Type: application/json" http://admin:9988@45.113.233.239:5984/_cluster_setup -d '{"action": "finish_cluster"}'
#curl -X PUT "http://admin:9988@172.26.129.241:5984/_node/_local/_nodes/couchdb@172.26.131.22" -d {}
#curl -X PUT "http://admin:9988@172.26.129.241:5984/_node/_local/_nodes/couchdb@172.26.133.132" -d {}
#curl -X PUT "http://admin:9988@172.26.129.241:5984/mydatabase"
#curl -X POST -H "Content-Type: application/json" "http://admin:9988@172.26.129.241:5984/_cluster_setup" -d '{"action": "finish_cluster"}'