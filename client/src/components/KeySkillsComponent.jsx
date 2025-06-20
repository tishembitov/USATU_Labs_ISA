import React, { useState, useEffect } from "react";
import axios from "axios";
import { API_URL, GET_DATA_INTERVAL } from "./constants";

const KeySkillsComponent = () => {
    const [keySkillsData, setKeySkillsData] = useState([]);
    const [skills, setSkills] = useState([]);
    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');
    const [selectedSkills, setSelectedSkills] = useState([]);

    const handleDateFromChange = (event) => {
      setDateFrom(event.target.value);
    };
  
    const handleDateToChange = (event) => {
      setDateTo(event.target.value);
    };

    const handleSkillChange = (e) => {
      setSelectedSkills(Array.from(e.target.selectedOptions, (option) => option.value));
    };
  
    const handleSubmit = (event) => {
      event.preventDefault();
      getData();
    };
  
    const getData = () => {
      console.log('GET Request to: ' + API_URL + '/keyskills');
      axios.get(API_URL + '/keyskills', {
        params: {
          date_from: dateFrom,
          date_to: dateTo,
          skills: selectedSkills.join(","),
        },
      })
        .then(response => {
          setKeySkillsData(response.data.image);
          setSkills(response.data.skills);
        })
        .catch(error => {
          console.error(error);
          setKeySkillsData([]);
          setSkills([]);
        });
    };
  
    const renderData = () => {
      if (keySkillsData) {
        return (
          <div className="text-center">
          <h1 className="display-3">Ключевые навыки</h1>
          <div className="d-flex justify-content-center">
            <form onSubmit={handleSubmit} noValidate>
              <div className="container">
                <div className="row">
                  <div className="col-sm">
                    <div className="form-group" style={{ width: '250px' }}>
                      <label htmlFor="inputDate">Данные за период с:</label>
                      <input type="date" name="date_from" className="form-control" />
                    </div>
                  </div>
                  <div className="col-sm">
                    <div className="form-group" style={{ width: '250px' }}>
                      <label htmlFor="inputDate">Данные за период по:</label>
                      <input type="date" name="date_to" className="form-control" /><br />
                    </div>
                  </div>
                </div>
              </div>
              <div className="container">
                <label htmlFor="inputDate">Укажите навыки:</label><br />
                <select
                  className="js-example-basic-multiple"
                  name="skills[]"
                  multiple="multiple"
                  onChange={handleSkillChange}
                  value={selectedSkills}
                >
                  {skills.map((skill) => (
                    <option key={skill} value={skill}>
                      {skill}
                    </option>
                  ))}
                </select>
                <div className="col-sm">
                  <br />
                  <input type="submit" value="Искать" />
                </div>
              </div>
            </form>
          </div>
    
          <div className="text-center">
            {messages && (
              <ul className="flashes">
                {messages.map((message, index) => (
                  <h6 key={index} className="display-6">
                    {message}
                  </h6>
                ))}
              </ul>
            )}
            <img src={keySkillsData} alt="Bar dashboard" />
          </div>
        </div>
        );
      } else {
        return (
          <div className="uk-alert-danger">
            <a className="uk-alert-close"></a>
            <p>NO KEY SKILLS DATA</p>
          </div>
        );
      }
    };
  
    useEffect(() => {
      const intervalId = setInterval(() => getData(), GET_DATA_INTERVAL);
  
      return () => {
        clearInterval(intervalId);
      };
    }, []);
  
    return (
      <div>
        {renderData()}
      </div>
    );
  };
  
  export default KeySkillsComponent;