import dataclasses
import json
import os

import yaml


@dataclasses.dataclass
class CopypastaInput:
    name: str
    description: str | None = None
    default: str = ""

    def dict(self):
        return {"name": self.name, "description": self.description or self.name, "default": self.default}


@dataclasses.dataclass
class CopypastaData:
    id: str
    name: str
    inputs: list[CopypastaInput]
    text: str

    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "inputs": list(map(CopypastaInput.dict, self.inputs)),
            "text": self.text,
        }


def slugify(name: str):
    return "".join(filter(lambda x: x == "_" or x.isalnum(), name.replace(" ", "_")))


def main():
    copypastas: list[CopypastaData] = []
    id_checker: dict[str, str] = {}

    for copypasta in os.scandir("copypasta"):
        name, ext = os.path.splitext(copypasta.name)
        if ext == ".yaml" or ext == ".yml":
            # Duplicate check
            copypasta_id = slugify(name)
            if copypasta_id in id_checker:
                raise RuntimeError(
                    f"ID conflict of \"{copypasta_id}\", originally defined for {id_checker['copypasta_id']}"
                )
            id_checker[copypasta_id] = copypasta.path

            # YAMLize
            with open(copypasta.path, "r", encoding="UTF-8", newline="\n") as f:
                yamldata = yaml.load(f, Loader=yaml.Loader)

            copypastas.append(
                CopypastaData(
                    id=copypasta_id,
                    name=yamldata["name"],
                    inputs=[
                        CopypastaInput(
                            name=input["name"],
                            description=input.get("description", input["name"]),
                            default=input.get("default", ""),
                        )
                        for input in yamldata["inputs"]
                    ],
                    text=yamldata["text"],
                )
            )

    # JSONizie
    with open("copypasta.json", "w", encoding="UTF-8", newline="") as f:
        json.dump(list(map(CopypastaData.dict, copypastas)), f)


if __name__ == "__main__":
    main()
