import React from 'react';
import KeySkillsComponent from './components/KeySkillsComponent'; // Путь к компоненту KeySkills
import VacanciesComponent from './components/VacanciesComponent'; // Путь к компоненту Vacancies
import SalaryComponent from './components/SalaryComponent'; // Путь к компоненту Salary
import './App.css';

function App() {
  return (
    <div>
      <KeySkillsComponent image={keySkillsImageUrl} />
      <VacanciesComponent image={vacanciesImageUrl} />
      <SalaryComponent image={salaryImageUrl} />
    </div>
  );
};

export default App;
