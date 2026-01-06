# Popupservice ReadMe

This extension to the microservices demo by Google adds the popupservice microservice to the project.

## Functionality:

When the main page is loaded a popup appears and the frontend makes a request to the popupservice. The popupservice then returns the content for the popup
consisting of three image links for the outfit categories (Head, Top, Bottom) and a list of the three selected products fetched from the productscatalogservice.

This way the outfit recommendations in the popup can dynamically change when new products are added. (With the limited amount of products in the demo there are only 2 possible outfit combinations at the moment but adding more clothing products would drastically increase that number)

## How to build?

The build process is fully automated via skaffold. Simply use "skaffold dev" to build and deploy the application in developer mode.

Known Issues: The cartservice build fails on Apple silicon machines. Changing the yaml file to force this service to run emulated rather than native arm can fix this.

## How to test?

Run the unit tests bundled with this repository.

## How to deploy?

Use the "skaffold run" command after starting docker and a kubernetes cluster. Skaffold should automatically build and deploy all services including the new popupservice. Dependencies are automatically installed from the requirements.txt.

## How does observability work?

The popupservice uses jager for distributed tracing and logging. The traces can be viewed in the jaeger UI at http://localhost:16686 once the application is started.

After running skaffold use the following port-forward command to access the jaeger UI:
kubectl port-forward svc/jaeger 16686:16686

In the jaeger UI select "popupservice" to view the traces generated.

Logging is done via stdout and can be viewed using kubectl logs commands or via the skaffold terminal output. The logs are structured json logs containing useful information for debugging and severity levels.



