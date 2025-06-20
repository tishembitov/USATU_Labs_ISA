import React, { useState, useEffect } from "react";
import axios from "axios";
import { API_URL, GET_DATA_INTERVAL } from "./constants";

const VacancyComponent = () => {
    const [vacancyData, setVacancyData] = useState([]);
    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');

    const handleDateFromChange = (event) => {
      setDateFrom(event.target.value);
    };
  
    const handleDateToChange = (event) => {
      setDateTo(event.target.value);
    };
  
    const handleSubmit = (event) => {
      event.preventDefault();
      // Здесь вы можете вызвать функцию отправки запроса с текущими значениями dateFrom и dateTo
      getData();
    };
  
  
    const getData = () => {
      console.log('GET Request to: ' + API_URL + '/vacancies');
      axios.get(API_URL + '/vacancies', {
        params: {
          date_from: dateFrom,
          date_to: dateTo,
        },
      })
        .then(response => {
          setVacancyData(response.data.image);
        })
        .catch(error => {
          console.error(error);
          setVacancyData([]);
        });
    };
  
    const renderData = () => {
      if (vacancyData) {
        return (
          <div className="text-center">
            <h1 className="display-3">Количество вакансий по уровням</h1>
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
                        <input type="date" name="date_to" className="form-control" />
                      </div>
                    </div>
                    <div className="row">
                      <div className="col-sm">
                        <br />
                        <input type="submit" value="Искать" />
                      </div>
                    </div>
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
              <img src={vacancyData} alt="Pie dashboard" />
            </div>
          </div>
        );
      } else {
        return (
          <div className="uk-alert-danger">
            <a className="uk-alert-close"></a>
            <p>NO VACANCY DATA</p>
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
  
  export default VacancyComponent;