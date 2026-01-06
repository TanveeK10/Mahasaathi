tags: ["admin","data","rfid","cv","integration","AI"]

Admin Guidelines: Data Flows & Integration
This document outlines the data-flow architecture for integrating the festival's real-time safety systems.

1. Computer Vision (CV) / AI Crowd Management System (Live Police Feed) This system is not a demo; it is an active, real-time security operation run by Pune Police.   

Data Source: Live video feeds from 400+ AI-enabled CCTV cameras deployed in the Peth areas.   

Processing:

Footage is fed into AI algorithms (based on models proven at the Kumbh Mela ) for real-time analysis.   

Models perform object detection (head/torso counting)  and mathematical modeling to achieve 90-95% accuracy in crowd density estimation and people flow vectoring.   

Data Output (To Admin Panel):

JSON Feed (Heatmap Data): { zone_id, timestamp, est_count, density_level (1-5), flow_vector (deg) }. This data is used by the RAG to answer "How crowded is Dagdusheth right now?"

Alerts: The core system is an Integrated Control & Command Centre (ICCC). When a zone's density_level exceeds a safety threshold (e.g., >4.5), the ICCC triggers an automatic alert.   

Admin Action: The admin panel must display this alert. The police response involves dispatching officers and making public announcements via IP Speakers.   

2. RFID Lost Person System (Proposed) This is a separate, proposed system for "lost and found".   

Data Source: Manual registration at entry points. { tag_id, user_name, guardian_contact } stored in a cloud database.   

Processing:

App-side (Report Missing): User reports tag_id as missing.

Field-side (Found Person): Officer with a reader scans tag_id.

Data Flow:

Officer's reader queries cloud DB with tag_id.

DB returns guardian_contact to officer's reader.   

Simultaneously, the DB pushes an alert to the Admin Panel: { tag_id, status: FOUND, location: officer_reader_gps }.

Admin panel updates the incident log and notifies the (panicked) guardian via the app that their loved one has been found.

3. Chatbot (RAG) Integration

The chatbot uses RAG to query the static .md files (like this one) for historical, logistical, and cultural questions.

The chatbot must also be connected to the dynamic JSON feed from the AI Crowd Management System to answer real-time questions about crowd levels.

The chatbot should not have direct access to the private RFID database. It can only query the incident log (e.g., "What is the status of incident #123?").