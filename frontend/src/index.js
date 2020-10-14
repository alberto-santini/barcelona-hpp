import React from 'react';
import ReactDOM from 'react-dom';
import AlgoliaPlaces from 'algolia-places-react';
import {Container, Row, Col, Form, Button, ListGroup, ListGroupItem} from 'react-bootstrap';

import './pis.scss'

class Page extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      fields: {
        neighbourhood: 'poblenou',
        sqm: '',
        rooms: '',
        state: 'need_renovation',
        elevator: 'true'
      },
      data: {
        price: null,
        upper_bound: null,
        lower_bound: null
      }
    }

    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleResult = this.handleResult.bind(this);
    this.submitForm = this.submitForm.bind(this);
  }

  handleInputChange(e) {
    this.setState({
      fields: { ...this.state.fields, [e.target.name]: e.target.value }
    });
  }

  handleResult(data) {
    this.setState({
      ...this.state, data
    })
  }

  submitForm(e) {
    e.preventDefault();

    var url = new URL('http://localhost:8000/');
    var params = this.state.fields;
    url.search = new URLSearchParams(params).toString();

    fetch(url, {method: 'GET'})
    .then(res => res.json())
    .then(data => this.handleResult(data));
  }

  render() {
    return (
      <Container>
        <Row>
          <Col md={1}></Col>
          <Col md={10} className="py-4">
            <header className="text-center">
              <img src="logo.svg" alt="Barcelona HPP"></img>
              <h1 className="h2 mt-4">Location Intelligence for Real Estate</h1>
            </header>
          </Col>
          <Col md={1}></Col>
        </Row>
        <Row>
          <Col md={1}></Col>
          <Col md={10}>
            <Form onSubmit={this.submitForm}>
              <Form.Group as={Row}>
                <Form.Label column sm={2}>Barri</Form.Label>
                <Col sm={10}>
                  <Form.Control
                    as="select"
                    name="neighbourhood"
                    value={this.state.fields.neighbourhood}
                    onChange={this.handleInputChange}
                  >
                    <option value="poblenou">Poblenou</option>
                    <option value="sarria">Sarrià</option>
                  </Form.Control>
                </Col>
              </Form.Group>
              <Form.Group as={Row}>
                <Form.Label column sm={2}>Adreça</Form.Label>
                <Col sm={10}>
                <AlgoliaPlaces
                    placeholder="Carrer de..."
                    options={{
                        appId: 'pl0RMHINOPC7',
                        apiKey: 'ee69abf250ec4f19adcc5e4e13b8ef62',
                        countries: ['es'],
                        aroundLatLngViaIP: false,
                        aroundLatLng: '41.404507,2.162822',
                        aroundRadius: 10*1000
                    }}
                />
                </Col>
              </Form.Group>
              <Form.Group as={Row}>
                <Form.Label column sm={2}>Metres quadrats</Form.Label>
                <Col sm={10}>
                  <Form.Control
                    required
                    name="sqm"
                    type="number"
                    placeholder="Superficie útil"
                    value={this.state.fields.sqm}
                    onChange={this.handleInputChange}
                  ></Form.Control>
                </Col>
              </Form.Group>
              <Form.Group as={Row}>
                <Form.Label column sm={2}>
                  Habitacions
                </Form.Label>
                <Col sm={10}>
                  <Form.Control
                    required
                    name="rooms"
                    type="number"
                    placeholder="Excluient menjador, cuina, banys, passadís, etc."
                    value={this.state.fields.rooms}
                    onChange={this.handleInputChange}
                  ></Form.Control>
                </Col>
              </Form.Group>
              <Form.Group as={Row}>
                <Form.Label column sm={2}>
                  Estat
                </Form.Label>
                <Col sm={4}>
                  <Form.Control
                    as="select"
                    name="state"
                    value={this.state.fields.state}
                    onChange={this.handleInputChange}
                  >
                    <option value="need_renovation">Necessita reforma</option>
                    <option value="second_hand">Per entrar a viure</option>
                    <option value="new">Per estrenar</option>
                  </Form.Control>
                </Col>
                <Form.Label column sm={2}>
                  Ascensor
                </Form.Label>
                <Col sm={4}>
                  <Form.Control
                    as="select"
                    name="elevator"
                    value={this.state.fields.elevator}
                    onChange={this.handleInputChange}
                  >
                    <option value="true">Si</option>
                    <option value="false">No</option>
                  </Form.Control>
                </Col>
              </Form.Group>
              <Form.Group as={Row}>
                <Form.Label column sm={2}>
                  Planta baixa
                </Form.Label>
                <Col sm={4}>
                  <Form.Control as="select">
                    <option value="true">Si</option>
                    <option value="false">No</option>
                  </Form.Control>
                </Col>
                <Form.Label column sm={2}>
                  Ultima planta
                </Form.Label>
                <Col sm={4}>
                  <Form.Control as="select">
                    <option value="true">Si</option>
                    <option value="false">No</option>
                  </Form.Control>
                </Col>
              </Form.Group>
              <Form.Group as={Row}>
                <Col>
                    <Button type="submit" className="w-100">Calcular</Button>
                </Col>
              </Form.Group>
            </Form>
          </Col>
          <Col md={1}></Col>
        </Row>
        <Row className="my-4">
          <Col md={1}></Col>
          <Col md={10} className="results">
            <Results data={this.state.data}></Results>
          </Col>
          <Col md={1}></Col>
        </Row>
      </Container>
    );
  }
}

class Results extends React.Component {
  render() {
    var prediction = null, comparative = null, similar = null;

    if(this.props.data.prediction) {
      prediction = (
        <ListGroup>
          <ListGroupItem variant="success" className="text-center">
            <p>
              Un bon preu per aquest pis és:
            </p>
            <p className="price">
              &lt; {this.props.data.prediction.lower_bound}&euro;
            </p>
          </ListGroupItem>
          <ListGroupItem variant="warning" className="text-center">
            <p>
              Un preu acceptable per aquest pis és:
            </p>
            <p className="price">
              {this.props.data.prediction.cost}&euro;
            </p>
          </ListGroupItem>
          <ListGroupItem variant="danger" className="text-center">
            <p>
              Un preu excessiu per aquest pis és:
            </p>
            <p className="price">
              &gt; {this.props.data.prediction.upper_bound}&euro;
            </p>
          </ListGroupItem>
        </ListGroup>
      );
    }

    if(this.props.data.comparative) {
      comparative = (
        <>
          <header className="mt-4">
            <h1 className="h3 text-center">
              En aquest barri...
            </h1>
          </header>
          <ListGroup>
            <ListGroupItem className="text-center">
              <p>
                Pisos amb la mateixa superfície es venen per gairebé
              </p>
              <p className="price">
                {this.props.data.comparative.by_sqm}&euro;
              </p>
            </ListGroupItem>
            <ListGroupItem className="text-center">
              <p>
                Pisos amb el mateix nombre d'habitacions es venen per gairebé
              </p>
              <p className="price">
                {this.props.data.comparative.by_rooms}&euro;
              </p>
            </ListGroupItem>
            <ListGroupItem className="text-center">
              <p>
                Pisos en el mateix estat es venen per gairebé:
              </p>
              <p className="price">
                {this.props.data.comparative.by_state}&euro;
              </p>
            </ListGroupItem>
          </ListGroup>
        </>
      );
    }

    if(this.props.data.similar) {
      const listItems = this.props.data.similar.map((item) =>
        <ListGroupItem>
          <header>
            <h1 className="h5">
              <a href={item.url}>{item.title}</a>
            </h1>
          </header>
          <p>
            {item.sqm} m<sup>2</sup>,&nbsp;
            {item.rooms} habitacions,&nbsp;
            <strong>{item.price}&euro;</strong>
          </p>
        </ListGroupItem>
      )

      similar = (
        <>
          <header className="mt-4">
            <h1 className="h3 text-center">També et pot interessar...</h1>
          </header>
          <ListGroup>
            {listItems}
          </ListGroup>
        </>
      );
    }

    return <>
      {prediction ? prediction : ''}
      {comparative ? comparative : ''}
      {similar ? similar : ''}
    </>;
  }
}

ReactDOM.render(<Page />, document.querySelector('#root'));