# DisasterRecoveryKubernetes
Event Driven Failure Recovery for Distributed Container Clusters

Following project enhances the capabilities of Kubernetes to ensure disaster recovery by an event driven approach using Stackstorm.
Stackstorm senses the availability of the nodes at Kubernetes master for the required resource provisioning and provisions resources in case of disasters to meet the requirements and triggers a series of workflow to create the required resources (EC2) by making API calls to the cloud provider (AWS). 

This architecture can also serve as a baseline for utilizing the spot instances for your Kubernetes deployment, minimizing the CAPEX on deploying the servers by triggering calls for provisioning as per preset sensors.

The architecture is cloud neutral and can be used for achieving Kubernetes DR on different cloud providers like Azure, Openstack, Google cloud, etc.

1.	Disable the iptables on each node to avoid conflicts with docker iptables
	a.	systemctl stop firewalld
	b.	systemctl disable firewalld

2.	Install NTP & make sure it is enabled & running
	a.	yum -y install ntp
	b.	systemctl start ntpd
	c.	systemctl enable ntpd

3.	Setting up the Kubernetes master
	a.	yum -y install etcd kubernetes

4.	Configure etcd to listen to all IP addresses inside /etc/etcd/etcd.conf
	a.	ETCD_NAME=default
	b.	ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
	c.	ETCD_LISTEN_CLIENT_URLS="http://0.0.0.0:2379"
	d.	ETCD_ADVERTISE_CLIENT_URLS=http://localhost:2379

5.	Configure Kubernetes API server inside /etc/kubernetes/apiserver
	a.	KUBE_API_ADDRESS="--address=0.0.0.0"
	b.	KUBE_API_PORT="--port=8080"
	c.	KUBELET_PORT="--kubelet_port=10250"
	d.	KUBE_ETCD_SERVERS="--etcd_servers=http://127.0.0.1:2379"
	e.	KUBE_SERVICE_ADDRESSES="--service-cluster-ip-range=10.254.0.0/16"
	f.	KUBE_ADMISSION_CONTROL="--admission_control=NamespaceLifecycle,NamespaceExists,LimitRanger,SecurityContextDeny,ResourceQuota"
	g.	KUBE_API_ARGS=""

6.	Start and enable etcd, kube-apiserver, kube-controller-manager and kube-scheduler
	a.	for SERVICES in etcd kube-apiserver kube-controller-manager kube-scheduler; do
			systemctl restart $SERVICES
			systemctl enable $SERVICES
			systemctl status $SERVICES 
		done

7.	Define flannel network configuration in etcd. This configuration will be pulled by flannel service on minions
	a.	etcdctl mk /atomic.io/network/config '{"Network":"172.17.0.0/16"}'

8.	Setting up Kubernetes Minions (Nodes)
	a.	Install flannel and Kubernetes using yum
		i.	yum -y install flannel kubernetes
	b.	Configure etcd server for flannel service. Update the following line inside /etc/sysconfig/flanneld to connect to the respective master
		i.	FLANNEL_ETCD="http://<master-ip>:2379"
	c.	Configure Kubernetes default config at /etc/kubernetes/config
		i.	KUBE_MASTER="--master=http://<master-ip>:8080"
	d.	Configure kubelet service inside /etc/kubernetes/kubelet
		i.	Minion1:
			KUBELET_ADDRESS="--address=0.0.0.0"
			KUBELET_PORT="--port=10250"
			KUBELET_HOSTNAME="--hostname_override=<self-ip>"
			KUBELET_API_SERVER="--api_servers=http://<master-ip>:8080"
			KUBELET_ARGS=""
		ii.	Minion2:
			KUBELET_ADDRESS="--address=0.0.0.0"
			KUBELET_PORT="--port=10250"
			KUBELET_HOSTNAME="--hostname_override=<self-ip>"
			KUBELET_API_SERVER="--api_servers=http://<master-ip>:8080"
			KUBELET_ARGS=""
	e.	Start and enable kube-proxy, kubelet, docker and flanneld services
		i.	for SERVICES in kube-proxy kubelet docker flanneld; do
				systemctl restart $SERVICES
				systemctl enable $SERVICES
				systemctl status $SERVICES 
			done
	f.	On each minion, you should notice that you will have two new interfaces added, docker0 and flannel0. You should get different range of IP addresses on flannel0 interface on each minion.
		i.	ip a | grep flannel | grep inet

9.	Now login to Kubernetes master node and verify the minions’ status
	a.	kubectl get nodes

10.	Command to create pods and replication controller
	a.	kubectl run my-nginx --image=nginx --replicas=2 --port=80

11.	Command to scale the pods
	a.	kubectl scale rc NAME --replicas=COUNT
