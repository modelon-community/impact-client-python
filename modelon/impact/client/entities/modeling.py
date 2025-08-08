from typing import List, Optional

from modelon.impact.client.configuration import Experimental
from modelon.impact.client.entities.model import Model
from modelon.impact.client.entities.package import Package
from modelon.impact.client.options import CompilerOptions, RuntimeOptions
from modelon.impact.client.sal.modeling import ModelingService
from modelon.impact.client.sal.service import Service


class ModelingSession:
    """Class containing ModelingService functionalities."""

    def __init__(
        self,
        session_id: str,
        workspace_id: str,
        modeling_sal: ModelingService,
        service: Service,
    ):
        self._session_id = session_id
        self._workspace_id = workspace_id
        self._modeling_sal = modeling_sal
        self._sal = service

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, ModelingSession) and obj._session_id == self._session_id

    def __repr__(self) -> str:
        return f"Modeling session with ID '{self._session_id}'"

    def close(self) -> None:
        return self._modeling_sal.close_session()

    @Experimental
    def get_available_runtime_options(self) -> RuntimeOptions:
        return RuntimeOptions(self._modeling_sal.get_available_runtime_options(), "")

    @Experimental
    def get_available_compiler_options(self) -> CompilerOptions:
        return CompilerOptions(self._modeling_sal.get_available_compiler_options(), "")

    @Experimental
    def get_packages(self) -> List[Package]:
        libraries = self._modeling_sal.get_top_classes()
        packages = []
        for project_id, top_classes in libraries.items():
            for top_class in top_classes:
                packages.append(
                    Package(
                        top_class["name"],
                        self._workspace_id,
                        project_id,
                        self._sal,
                        self._modeling_sal,
                    )
                )
        return packages

    @Experimental
    def get_experiment_definitions(self, class_path: str) -> dict:
        project_ids = [prj.get("id") for prj in self._modeling_sal.get_projects()]
        return self._modeling_sal.get_experiment_definitions(project_ids, class_path)

    @Experimental
    def find_usage(self, modelica_path: str) -> List[str]:
        return self._modeling_sal.find_usage(modelica_path)

    @Experimental
    def get_model_parmeters(self, modelica_path: str) -> List[str]:
        return self._modeling_sal.get_model_parmeters(modelica_path)

    @Experimental
    def create_top_level_package(
        self, project_id: str, package_name: str, libraryToExtend: Optional[str] = None
    ) -> Package:
        self._modeling_sal.create_top_level_package(
            project_id, package_name, libraryToExtend
        )
        return Package(
            package_name,
            self._workspace_id,
            project_id,
            self._sal,
            self._modeling_sal,
        )

    @Experimental
    def duplicate_modelica_model(
        self,
        source_modelica_path: str,
        target_modelica_path: str,
    ) -> Model:
        source_modelica_path_split = source_modelica_path.split(".")
        target_modelica_path_split = target_modelica_path.split(".")
        source_library_name = source_modelica_path_split[0]
        target_library_name = target_modelica_path_split[0]
        top_level_packages = self.get_packages()
        package_name_prj_id_map = {
            package.name: package.project_id
            for package in top_level_packages  # type: ignore
        }
        if source_library_name not in package_name_prj_id_map:
            raise ValueError(f"Source library {source_library_name} doesn't exist")
        if target_library_name not in package_name_prj_id_map:
            raise ValueError(f"Target library {target_library_name} doesn't exist")

        source_project_id = package_name_prj_id_map[source_library_name]
        target_project_id = package_name_prj_id_map[target_library_name]
        result = self._modeling_sal.duplicate_modelica_model(
            source_project_id=source_project_id,
            old_name=source_modelica_path,
            target_project_id=target_project_id,
            new_name=target_modelica_path_split[-1],
            target_package_name=target_modelica_path_split[-2],
        )
        return Model(
            result["newClassName"], self._workspace_id, target_project_id, self._sal
        )
