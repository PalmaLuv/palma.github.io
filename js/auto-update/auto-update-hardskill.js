async function fetchInJson(url) {
    const response = await fetch(url);
    return await response.json();
}

async function UpdateHardSkill() {
    const skillsList = await fetchInJson(
        (await fetchInJson("./.github/file/list-file.json")).git_hardskill
    )

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