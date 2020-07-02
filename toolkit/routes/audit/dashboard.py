import json
import math
from datetime import datetime

from flask import current_app as app
from flask import redirect, request, url_for, render_template
from sqlalchemy import func

from toolkit import dbAlchemy as db
from toolkit.controller.seo.lighthouse import audit_google_lighthouse_full
from toolkit.models import Audit, LighthouseScore

@app.template_filter('formatdatetime')
def format_datetime(value, format="%d %b %Y %I:%M %p"):
    """Format a date time to (Default): d Mon YYYY HH:MM P"""
    if value is None:
        return ""
    return value.strftime(format)

@app.route('/audit', methods=["GET"])
def audit_home():
    return render_template("audit/audit.jinja2")

@app.route('/audit/lighthouse/full')
def dashboard_audit_lighthouse_full():
    results = Audit.query.filter(Audit.type_audit == "Lighthouse_Full").all()
    result_arr={"results": []}
    for i in results:
        result_arr["results"].append({"id": i.id, "url": i.url, "result": i.result, "begin_date": i.begin_date})
    return result_arr

@app.route('/audit/lighthouse/full', methods=["POST"])
def add_audit_lighthouse_full():
    url = request.form['url']
    count = Audit.query.filter(Audit.url == url).filter(Audit.type_audit=="Lighthouse_Full").count()
    if url and count == 0:
        value = audit_google_lighthouse_full(url)
        new_audit = Audit(
            url = url, result=json.dumps(value), type_audit="Lighthouse_Full", begin_date=datetime.now()
        )
        db.session.add(new_audit)
        db.session.commit()
    return redirect(url_for('dashboard_audit_lighthouse_full'))

@app.route('/audit/lighthouse/score', methods=["POST"])
def add_audit_lighthouse_score():
    url = request.form['url']
    
    if url:
        value = audit_google_lighthouse_full(url)
        accessibility = int(math.floor(value["lighthouseResult"]["categories"]["accessibility"]["score"] * 100))
        seo = int(math.floor(value["lighthouseResult"]["categories"]["seo"]["score"] * 100))
        pwa = int(math.floor(value["lighthouseResult"]["categories"]["pwa"]["score"] * 100))
        best_practices = int(math.floor(value["lighthouseResult"]["categories"]["best-practices"]["score"] * 100))
        performance = int(math.floor(value["lighthouseResult"]["categories"]["performance"]["score"] * 100))
        new_score = LighthouseScore(
            url = url, accessibility=accessibility,pwa=pwa,seo=seo, best_practices=best_practices,performance=performance, begin_date=datetime.now()
        )
        db.session.add(new_score)
        db.session.commit()
    return redirect(url_for('dashboard_audit_lighthouse_score'))

@app.route('/audit/lighthouse/score')
def dashboard_audit_lighthouse_score():
    LS = LighthouseScore
    error = None
    quer = db.session.query(LS.id,LS.url, LS.accessibility, LS.pwa, LS.seo, LS.best_practices, LS.performance, func.max(LS.begin_date).label('begin_date')).group_by(LS.url)
    results = quer.all()
    result_arr={"results": []}
    if app.config['GOOGLE_API_KEY'] == "None":
        print("HAHAHA")
        error = True
    for i in results:
        result_arr["results"].append({"id": i.id, "url": i.url, "accessibility": i.accessibility, "pwa": i.pwa, "seo": i.seo, "best_practices": i.best_practices, "performance": i.performance, "begin_date": i.begin_date})
    return render_template("audit/lighthouse/lighthouse_all.jinja2", result=result_arr["results"], error=error)

@app.route('/audit/lighthouse/score/<id>', methods=["GET"])
def dashboard_audit_lighthouse_score_get_id(id):
    id_url = LighthouseScore.query.filter(LighthouseScore.id == id).first()
    results = LighthouseScore.query.filter(LighthouseScore.url == id_url.url).order_by(LighthouseScore.begin_date.desc()).all()

    result_arr={"results": []}
    for i in results:
        result_arr["results"].append({"id": i.id, "url": i.url, "accessibility": i.accessibility, "pwa": i.pwa, "seo": i.seo, "best_practices": i.best_practices, "performance": i.performance, "begin_date": i.begin_date})
    return render_template("audit/lighthouse/lighthouse.jinja2", url=id_url.url, id=id, result=result_arr["results"])



@app.route('/audit/lighthouse/score/all')
def dashboard_audit_lighthouse_score_all():
    LS = LighthouseScore
    results = LS.query.all()
    result_arr={"results": []}
    for i in results:
        result_arr["results"].append({"id": i.id, "url": i.url, "accessibility": i.accessibility, "pwa": i.pwa, "seo": i.seo, "best_practices": i.best_practices, "performance": i.performance, "begin_date": i.begin_date})
    return result_arr