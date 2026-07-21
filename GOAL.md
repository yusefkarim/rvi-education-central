I have been tasked with creating a centralized repository for RISC-V International that serves as a central hub for academics and professors to share and reuse lecture and training material.

I want this repository to be modern and highly structured, but I want the sturcture to be primarily managed and enforced through automation (GitHub actions)

The idea:

* A single central repository
* A single central README.md as the root that is automatically updated via GitHub actions
* Separate directory at the root per university/institution/company, let's call this a "resource directory"
    - Must follow a standarized naming convention, enforced by CI and code review
* For each resource directory, there are subdirectories relating to course lecture and/or lab lecture material
    - Each subdir must have a formal structure that is validated via GitHub actions
* There will be a central "common" (or better named) directory at the base of the repo that contains symbolic links to all shareavle images, diagrams, etc provided in each subdirectory of each "resource directory"
    - Symbolic links are automatically created via GitHub actions
    - The assets coming from each "resource directory" should be catergorizable in some way, and this will need proper thought (e.g., how to name or label assets in a low friction way to allow this?). See `./references/comparch-slides/common` for ideas

We need the create a completely grounded and solid plan for this idea. It is paramount that the approach is maintainable and low-friction, such that professors find it easy to use and will become willing to contribute to it. Given that the more formal/automated items (especially the linking of assets into a common folder) might take extra effort from the user, it might be OK to make it an opt-in feature of the repo (e.g., if they don't follow the standards, they are still welcome to add their resources, but will just have less visibility) - it would be cool if there is a way to automatically track and signify who is adhering to the standards and who is not (as a nice way to push people to adhere).


