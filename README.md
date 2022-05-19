# AbobeInterview

Parse YAML Config 
1. Problem: 
A user has a YAML file that defines their service's configuration for each  environment and region. The Ops team's tooling uses the YAML file to provision  and update the service, but the tooling only accepts a single environment/region  combination at a time. Write a script using your preferred language to reduce a  user's YAML file to a single environment/region combination according to input  parameters. 
2. Expectations: 
• Script reads YAML file from disk 
• Script accepts three inputs: a environment, a region and YAML file  location 
• Script uses configuration under the common key if the environment and/or  region input parameter does not exist as a key in the YAML file 
• Script sorts the keys of the reduced config alphabetically after  
service_name, team_name and cost_center 
• Script outputs reduced configuration as a JSON file 
• Script uploads JSON file to an S3 bucket and has exponential backoff  retry logic that will fail if the upload does not complete in 10m 
• Example 
3. Example Input YAML: 
apiVersion: v1
kind: Namespace
metadata:
  name: om
  labels:
    fico.application.owner: 'Origination_Manager'
    fico.application.version: '5.0'
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: application-accessing-service-{{instanceId}}
  namespace: om
  labels:
    app: application-accessing-service-{{instanceId}}
    fico.application.owner: 'Origination_Manager'
    fico.application.version: "5.0"
spec:
  replicas: 2
  strategy:
      rollingUpdate:
        maxSurge: 1
        maxUnavailable: 0
      type: RollingUpdate
  selector:
    matchLabels:
      app: application-accessing-service-{{instanceId}}
  template:
    metadata:
      labels:
        app: application-accessing-service-{{instanceId}}
    spec:
      containers:
        - image: '@image.repo@/@image.name@:@image.tag.dmp@'
          imagePullPolicy: Always
          name: deployment
          readinessProbe:
            exec:
              command:
              - /bin/python
              - /tmp/healthcheck.py
            initialDelaySeconds: 400
            periodSeconds: 20
            failureThreshold: 5
            timeoutSeconds: 40
          livenessProbe:
            exec:
              command:
              - /bin/python
              - /tmp/healthcheck.py
            initialDelaySeconds: 400
            failureThreshold: 5
            periodSeconds: 20
            timeoutSeconds: 400
          env:
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
            - name: IAM_POST_LOGOUT_URL
              value: https://console.{{deploymentZone}}
          ports:
            - containerPort: 8080
              name: http
              protocol: TCP
          resources:
            requests:
              cpu: "4"
              memory: 8Gi                 
      affinity: 
        podAntiAffinity: 
          preferredDuringSchedulingIgnoredDuringExecution: 
            - 
              podAffinityTerm: 
                labelSelector: 
                  matchExpressions: 
                    - 
                      key: app
                      operator: In
                      values: 
                        - om
                    - 
                      key: fico.application.owner
                      operator: In
                      values: 
                        - Origination_Manager
                topologyKey: failure-domain.beta.kubernetes.io/zone
              weight: 100
      dnsPolicy: ClusterFirst
      restartPolicy: Always            
---
apiVersion: v1
kind: Service
metadata:
  name: application-accessing-service-{{instanceId}}
  namespace: om
  labels:
    app: application-accessing-service-{{instanceId}}
    fico.application.owner: 'Origination_Manager'
    fico.application.version: '5.0'
spec:
  selector:
    app: application-accessing-service-{{instanceId}}
  ports:
  - name: http
    protocol: TCP
    port: 8080
    targetPort: 8080
---
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: application-accessing-service-{{instanceId}}
  namespace: om
  labels:
    app: application-accessing-service-{{instanceId}}
    fico.application.owner: 'Origination_Manager'
    fico.application.version: '5.0'
spec:
  rules:
  - host: 'om-{{instanceId}}.{{deploymentZone}}'
    http:
        paths:
        - backend:
            serviceName: application-accessing-service-{{instanceId}}
            servicePort: 8080
            
            
4. Example: Here’s what a running script should look like sh-session: 
some_script dev va6 /some/path/to/config.yaml 
Output Json: 
json 
{ 
 "environment": "dev", 
 "region": "va6", 
 "configuration": { 
 "service_name": "some-service", 
 "team_name": "Some Team", 
 "cost_center": 1564577, 
 "helm": {
 "chart_name": "some-chart", 
 "helm_version": "3", 
 "release_name": "sc", 
 "values": "/some/path/in/some-repo/dev/va6.yaml", 
 }, 
 "notifications": { 
 "deployments": "#some-channel-deployments", 
 "releases": "#some-channel-releases" 
 }, 
 "repo": { 
 "url": "git@git.corp.adobe.com:some-org/some-repo.git", 
 "version": "main" 
 } 
 } 
}  
5. General Rules: 
Please note that Adobe has considerable experience with publicly available  examples. We realize 
that many implementations exist on the Internet and are very familiar with them.  We will not 
hold copying existing source code against you since in real-life leveraging  existing code may, at 
times, be the best and quickest way to get a good result. Be aware though that  not all publicly 
available solutions are of good code quality and we will consider your choice as  part of the 
assessment. We will also not hold it against you if you choose to write the entire  example from 
scratch. If you do decide to copy code from third party resources, please  consider the following 
when submitting your code: 
• Declare which parts of the sample is your own code 
• Reference all copied code and where you took it from: do not remove  copyrights or comments. Any violation of copyrights or obfuscation tactics  will reflect negatively on your assessment.
6. Please provide us with a link from where we can download your solutions. For  technical reasons we cannot accept email attachments.
