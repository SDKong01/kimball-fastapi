VERSION :=  # Define the version here when calling make (e.g., make build VERSION=1.0)

# Target tasks
build:
	python setup.py bdist_wheel

install:
	pip install --upgrade pip && \
	    pip install -r requirements.txt
	#pip install dist/orion_digital_twin_app-$(VERSION)-py3-none-any.whl

clean:
	rm -rf build dist *.egg-info

help:
	@echo "Available targets:"
	@echo "  build          Build the package"
	@echo "  install        Install the package"
	@echo "  clean          Clean build artifacts"
