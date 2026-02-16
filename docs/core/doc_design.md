# Documentation design


- Documentation is done in separated space, `<project-name>/docs/` which mirrors the `<project-name>/src/` space: files, instances. Inside this mirrored folder, `.hat` extensions are replaced by `.md` ones.
- On CLI, there is a command for updating the project that will automatically generate the `.md` files for all the `.hat` files generated and fill them with the instance headers/properties to be filled with descriptions by the user.
- The main idea is to remove the documentation pollution inside the code files and provide a clear and automated space for writing proper documentation.
- On further scans of the CLI's updating command, it may enforce invalid instance fields (that maybe were updated in the code but not on documentation) and even preventing from building the project for release if they are not fixed.
