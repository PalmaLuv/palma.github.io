async function fetchProjects(username) {
    const response = await fetch(`https://api.github.com/users/${username}/repos`);
    return await response.json(); 
}

async function fetchProject(username, repoName) {
    try {
        const response = await fetch(`https://api.github.com/repos/${username}/${repoName}`);
        console.log(`https://api.github.com/repos/${username}/${repoName}`);
        return await response.json();
    } catch (error) {
        console.error(`Ошибка при обращении к API для репозитория ${repoName}:`, error);
        return await null;
    }
}

async function fetchGitsProjects(gitUrl) {
    const responce = await fetch(gitUrl);
    return await responce.json();
}

async function updatePortfolio() {
    const gitUrl = "https://gist.githubusercontent.com/PalmaLuv/a563f27ec9dbb989b1872832acc8401c/raw/94dfaf34d6f11e4ad81261dc85223c323e1c0ad7/potrfolio_project-list.json"; 
    const projectsContainer = document.getElementById("projects");

    const githubProjects = await fetchGitsProjects(gitUrl);
    
    githubProjects.forEach(
        async (element) => 
        { 
            console.log(element);

            const imageUrl = element.urlIMG == "NONE" ?
                `https://opengraph.githubassets.com/1/${element.username}/${element.name}` 
              : element.urlIMG;

            const repoElement = await fetchProject(
                element.username,
                element.name
            )

            const projectElement = document.createElement("li");
            projectElement.className = "project"; 
            projectElement.innerHTML = `
                <a href="${repoElement.html_url}"> 
                    <img class="project__img" src="${imageUrl}">
                    <div class="project__title-container">
                      <h3 class="project__title">${repoElement.name}</h3>
                      <div class="project__star__inf"> 
                                <scan class="star_inf-num">${repoElement.stargazers_count}</scan>
                                <svg aria-hidden="true" viewBox="0 0 16 16" version="1.1" data-view-component="true" class="star_svg">
                                    <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Zm0 2.445L6.615 5.5a.75.75 0 0 1-.564.41l-3.097.45 2.24 2.184a.75.75 0 0 1 .216.664l-.528 3.084 2.769-1.456a.75.75 0 0 1 .698 0l2.77 1.456-.53-3.084a.75.75 0 0 1 .216-.664l2.24-2.183-3.096-.45a.75.75 0 0 1-.564-.41L8 2.694Z"></path>
                                </svg>
                            </div> 
                    </div>
                    <p class="project__text">${repoElement.description || "No description"}</p>
                </a>`;
            projectsContainer.appendChild(projectElement);
        });
}

document.addEventListener("DOMContentLoaded", () => { updatePortfolio(); });
