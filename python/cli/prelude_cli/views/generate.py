import json
import os

import click

from prelude_cli.views.shared import Spinner, pretty_print
from prelude_sdk.controllers.generate_controller import GenerateController
from prelude_sdk.models.codes import Control


@click.group()
@click.pass_context
def generate(ctx):
    """Generate tests"""
    ctx.obj = GenerateController(account=ctx.obj)


def _process_results(result: dict, output_dir: str, job_id: str) -> dict:
    if result["status"] == "COMPLETE":
        for technique in result["output"]:
            if technique["status"] == "SUCCEEDED":
                technique_directory = technique["technique"].replace(".", "_")
                os.makedirs(f"{output_dir}/{technique_directory}")
                content = technique.get("ai_generated") or technique.get(
                    "existing_test"
                )
                with open(f"{output_dir}/{technique_directory}/test.go", "w") as f:
                    f.write(content["go_code"])
                for i, sigma_rule in enumerate(content["sigma_rules"]):
                    with open(
                        f"{output_dir}/{technique_directory}/sigma_{i}.yaml", "w"
                    ) as f:
                        f.write(sigma_rule)
                for i, query in enumerate(content.get("threat_hunt_queries", [])):
                    with open(
                        f"{output_dir}/{technique_directory}/query_{i}.json", "w"
                    ) as f:
                        json.dump(
                            dict(name=query["name"], query=query["query"]), f, indent=4
                        )
                with open(f"{output_dir}/{technique_directory}/config.json", "w") as f:
                    json.dump(
                        dict(
                            technique=technique["technique"],
                            name=technique["name"],
                            unit="response",
                        ),
                        f,
                        indent=4,
                    )
                if content["readme"]:
                    with open(
                        f"{output_dir}/{technique_directory}/README.md", "w"
                    ) as f:
                        f.write(content["readme"])
        return dict(
            output_dir=output_dir,
            successfully_generated=[
                t["technique"] for t in result["output"] if t["status"] == "SUCCEEDED"
            ],
            failed=[
                t["technique"] for t in result["output"] if t["status"] == "FAILED"
            ],
            job_id=job_id,
        )
    else:
        raise Exception(
            "Failed to generate threat intel: %s (ref: %s)", result["reason"], job_id
        )


@generate.command("threat-intel")
@click.argument(
    "threat_pdf",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.argument(
    "output_dir", type=click.Path(dir_okay=True, file_okay=False, writable=True)
)
@click.pass_obj
@pretty_print
def generate_threat_intel(
    controller: GenerateController, threat_pdf: str, output_dir: str
):
    with Spinner("Uploading") as spinner:
        job_id = controller.upload_threat_intel(threat_pdf)["job_id"]
        spinner.update(spinner.task_ids[-1], description="Parsing PDF")
        while (result := controller.get_threat_intel(job_id)) and result[
            "status"
        ] == "RUNNING":
            if result["step"] == "GENERATE":
                spinner.update(
                    spinner.task_ids[-1],
                    description=f'Generating ({result["completed_tasks"]}/{result["num_tasks"]})',
                )
    return _process_results(result, output_dir, job_id)


@generate.command("from-advisory")
@click.argument(
    "partner", type=click.Choice([Control.CROWDSTRIKE.name], case_sensitive=False)
)
@click.option(
    "-a", "--advisory_id", required=True, type=str, help="Partner advisory ID"
)
@click.option(
    "-o",
    "--output_dir",
    required=True,
    type=click.Path(dir_okay=True, file_okay=False, writable=True),
)
@click.pass_obj
@pretty_print
def generate_from_partner_advisory(
    controller: GenerateController, partner: Control, advisory_id: str, output_dir: str
):
    with Spinner("Uploading") as spinner:
        job_id = controller.generate_from_partner_advisory(
            partner=Control[partner], advisory_id=advisory_id
        )["job_id"]
        spinner.update(spinner.task_ids[-1], description="Parsing PDF")
        while (result := controller.get_threat_intel(job_id)) and result[
            "status"
        ] == "RUNNING":
            if result["step"] == "GENERATE":
                spinner.update(
                    spinner.task_ids[-1],
                    description=f'Generating ({result["completed_tasks"]}/{result["num_tasks"]})',
                )
    return _process_results(result, output_dir, job_id)
