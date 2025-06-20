import React, { useState, useEffect } from "react";
import axios from "axios";
import { API_URL, GET_DATA_INTERVAL } from "./constants";

const SalaryComponent = () => {
    const [salaryData, setSalaryData] = useState([]);
  
    const getData = () => {
      console.log('GET Request to: ' + API_URL + '/salary');
      axios.get(API_URL + '/salary')
        .then(response => {
          setSalaryData(response.data.image);
        })
        .catch(error => {
          console.error(error);
          setSalaryData([]);
        });
    };
  
    const renderData = () => {
      if (salaryData) {
        return (
          <div className="text-center">
            <h1 className="display-3">Распределение зарплат по уровням</h1>
            <img src={salaryData} alt="Salary Dashboard" />
          </div>
        );
      } else {
        return (
          <div className="uk-alert-danger">
            <a className="uk-alert-close"></a>
            <p>NO SALARY DATA</p>
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
  
  export default SalaryComponent;