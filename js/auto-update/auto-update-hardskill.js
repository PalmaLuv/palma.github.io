async function fetchInJson(url) {
    const response = await fetch(url);
    return await response.json();
}

async function UpdateHardSkill() {
    const gitUrl = "https://gist.githubusercontent.com/PalmaLuv/a563f27ec9dbb989b1872832acc8401c/raw/portfolio_hardskill-list.json"
    const skillsList = await fetchInJson(gitUrl)

    const hardSkillContainer = document.getElementById("hard__skill-list");
    (skillsList.skills).forEach(element => { 
        GetJsonElement(element.array, element.name, hardSkillContainer)
    });
}

function GetJsonElement(array, titleName, object) { 
    const title = document.createElement("div"); 
    title.className = "skill-element__block";
    title.innerHTML = `<h3>${titleName}</h3>`;

    const list_skils = document.createElement("ul"); 
    list_skils.className = "list__skills";

    array.forEach(element => { 
        const skillElement = document.createElement("li");
        skillElement.innerHTML = `${element}`
        list_skils.appendChild(skillElement);
    });

    title.appendChild(list_skils);
    object.appendChild(title);
}

document.addEventListener("DOMContentLoaded", () => {
    UpdateHardSkill();
});