# Popupservice ReadMe

This extension to the microservices demo by Google adds the popupservice microservice to the project.

## Functionality:

When the main page is loaded a popup appears and the frontend makes a request to the popupservice. The popupservice then returns the content for the popup
consisting of three image links for the outfit categories (Head, Top, Bottom) and a list of the three selected products fetched from the productscatalogservice.

This way the outfit recommendations in the popup can dynamically change when new products are added. (With the limited amount of products in the demo there are only 2 possible outfit combinations at the moment but adding more clothing products would drastically increase that number)

## How to build?

The build process is fully automated via skaffold. Simply use "skaffold dev" to build and deploy the application in developer mode.

## How to test?

The popupservice includes comprehensive unit tests in "test_popup_main.py" that validate all core functions including outfit recommendations, random item selection, fallback behavior, and tracing initialization. Navigate to the "src/popupservice" directory and run "python test_popup_main.py" to execute the tests. 
The tests use Python's built-in "unittest" framework with mocked external dependencies (gRPC, OpenTelemetry), so no additional services need to be running.

## How to deploy?

Use the "skaffold run" command after starting docker and a kubernetes cluster. Skaffold should automatically build and deploy all services including the new popupservice. Dependencies are automatically installed from the requirements.txt.

## How does observability work?

The popupservice uses jager for distributed tracing and logging. The traces can be viewed in the jaeger UI at http://localhost:16686 once the application is started.

After running skaffold use the following port-forward command to access the jaeger UI:
kubectl port-forward svc/jaeger 16686:16686

In the jaeger UI select "popupservice" to view the traces generated.

Logging is done via stdout and can be viewed using kubectl logs commands or via the skaffold terminal output. The logs are structured json logs containing useful information for debugging and severity levels.

## FIXES

If the microservice "redis" fails to build, you need to manually pull via "docker pull https://docker.io/library/redis:6.2-alpine" (a docker account is needed)

