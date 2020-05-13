import React from 'react';
import './App.css';

function League({league, selected, onSelected}) {
    return (
        <div className="col my-2" onClick={onSelected.bind(this, league)}>
            <div id={league.slug}
                 className={'card text-center h-100 bg-light league-button ' + ((selected) ? 'clicked' : '')}>
                <div>{selected}</div>
                <img
                    src={'/assets/img/' + league.slug + '.png'}
                    className="card-img-top bg-dark"
                    alt={league.name}
                />
                <div className="p-2 my-auto">
                    <h5 className="card-text">{league.name}</h5>
                </div>
            </div>
        </div>
    );
}

class Page extends React.Component {
    constructor(props) {
        super(props);

        this.handleSelectLeague = this.handleSelectLeague.bind(this);

        this.state = {
            leagues: [],
            selected: {},
        };
    }

    componentDidMount() {
        this.loadInitialData();
    }

    async loadInitialData() {
        const request = await fetch('/api/leagues');
        const data = await request.json();
        console.log(data);
        this.setState({
            leagues: data.leagues,
        });
    }

    handleSelectLeague(league) {
        this.setState(({selected}, props) => {
            return {
                selected: {...selected, [league.slug]: (!selected[league.slug])},
            };
        });
    }

    calendarUrl() {
        let leagues = this.selectedLeagues();
        if (leagues.length === 0) {
            return '#'
        }
        return `/api/query-leagues?leagues=${leagues.join(",")}`;
    }

    selectedLeagues() {
        return Object.keys(this.state.selected).filter((slug) => this.state.selected[slug]).sort();
    }

    render() {
        return (
            <div className="container">
                <div className="row">
                    <div className="col text-center m-2">
                        <h1>LoL eSports Calendar Generator</h1>
                    </div>
                </div>
                <div className="row">
                    <div className="col alert alert-primary mx-3 text-center">
                        <span>Your link: {this.selectedLeagues().length === 0 && 'Select some leagues!'}</span>
                        <a id="calendar_url" href={this.calendarUrl()}>{this.selectedLeagues().join(', ')}</a>
                    </div>
                </div>
                <div className="row row-cols-2 row-cols-sm-3 row-cols-md-4 row-cols-lg-5 row-cols-xl-6">
                    {this.state.leagues.map((league) =>
                        <League key={league.slug} league={league} selected={this.state.selected[league.slug]}
                                onSelected={this.handleSelectLeague}/>
                    )}
                </div>
                <div className="row">
                    <div className="col text-center">
                        <p><a href="https://github.com/asherdavidson/lol_esports_calendar_generator">Source Code</a></p>
                    </div>
                </div>
            </div>
        );
    }
}

export default Page;
