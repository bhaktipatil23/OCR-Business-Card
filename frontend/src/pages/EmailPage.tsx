import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Navbar from "@/components/layout/Navbar";
import { toast } from "sonner";

interface ExtractedData {
  name: string;
  phone: string;
  email: string;
  company: string;
  designation: string;
  address: string;
}

const EmailPage = () => {
  const location = useLocation();
  const { eventData, extractedData } = location.state || {};
  
  const [selectedEvent, setSelectedEvent] = useState(eventData?.event || '');
  const [emailData, setEmailData] = useState({
    to: '',
    subject: 'Partnership Opportunity with ReCircle - Sustainable Business Solutions',
    body: `Dear Business Partner,\n\nI hope this email finds you well. I am writing to introduce you to ReCircle, an innovative company focused on sustainable business solutions and circular economy practices.\n\nReCircle specializes in:\n• Sustainable waste management solutions\n• Circular economy consulting\n• Environmental impact reduction strategies\n• Green technology implementation\n\nWe believe there could be excellent synergy between our organizations and would love to explore potential partnership opportunities.\n\nWould you be available for a brief call next week to discuss how we might collaborate?\n\nBest regards,\n${eventData?.name || 'Your Name'}\n${eventData?.team || 'Your Team'}`
  });
  const [filterType, setFilterType] = useState('send-all');
  const [selectedPeople, setSelectedPeople] = useState<string[]>([]);
  
  const events = [eventData?.event].filter(Boolean);
  const people: ExtractedData[] = extractedData || [];
  
  useEffect(() => {
    if (filterType === 'send-all') {
      setSelectedPeople(people.map(p => p.email).filter(Boolean));
    } else {
      setSelectedPeople([]);
    }
  }, [filterType, people]);
  
  const handlePersonToggle = (email: string) => {
    setSelectedPeople(prev => 
      prev.includes(email) 
        ? prev.filter(e => e !== email)
        : [...prev, email]
    );
  };
  
  const handleSendEmail = () => {
    if (selectedPeople.length === 0) {
      toast.error('Please select at least one recipient');
      return;
    }
    toast.success(`Email sent to ${selectedPeople.length} recipient(s)`);
  };
  
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 w-full mx-auto px-2 sm:px-4 lg:px-8 py-2 sm:py-4">
        <div className="max-w-4xl mx-auto space-y-3 sm:space-y-6">
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 px-2 sm:px-0">Send Email</h1>
          
          {/* Event Selection */}
          <div className="bg-white p-3 sm:p-4 rounded-lg border mx-2 sm:mx-0">
            <label className="block text-sm font-medium text-gray-700 mb-2">Select Event</label>
            <select 
              value={selectedEvent}
              onChange={(e) => setSelectedEvent(e.target.value)}
              className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Choose an event...</option>
              {events.map(event => (
                <option key={event} value={event}>{event}</option>
              ))}
            </select>
          </div>
          
          {/* Email Form */}
          <div className="bg-white p-3 sm:p-4 rounded-lg border mx-2 sm:mx-0 space-y-3 sm:space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">TO</label>
              <input 
                type="text"
                value={emailData.to}
                onChange={(e) => setEmailData({...emailData, to: e.target.value})}
                placeholder="Recipients will be auto-filled based on selection below"
                className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                readOnly
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">SUBJECT</label>
              <input 
                type="text"
                value={emailData.subject}
                onChange={(e) => setEmailData({...emailData, subject: e.target.value})}
                className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">BODY</label>
              <textarea 
                value={emailData.body}
                onChange={(e) => setEmailData({...emailData, body: e.target.value})}
                rows={8}
                className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 sm:rows-12"
              />
            </div>
          </div>
          
          {/* Filter Options */}
          <div className="bg-white p-3 sm:p-4 rounded-lg border mx-2 sm:mx-0">
            <h3 className="text-base sm:text-lg font-medium text-gray-900 mb-3 sm:mb-4">Send Options</h3>
            <div className="space-y-2 sm:space-y-3">
              <label className="flex items-center text-sm sm:text-base">
                <input 
                  type="radio" 
                  name="filter" 
                  value="send-all"
                  checked={filterType === 'send-all'}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="mr-2 sm:mr-3"
                />
                <span className="break-words">Send to All ({people.length} people)</span>
              </label>
              <label className="flex items-center text-sm sm:text-base">
                <input 
                  type="radio" 
                  name="filter" 
                  value="particular"
                  checked={filterType === 'particular'}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="mr-2 sm:mr-3"
                />
                <span>Send to Particular Person</span>
              </label>
              <label className="flex items-center text-sm sm:text-base">
                <input 
                  type="radio" 
                  name="filter" 
                  value="exclude"
                  checked={filterType === 'exclude'}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="mr-2 sm:mr-3"
                />
                <span>Exclude Person</span>
              </label>
            </div>
          </div>
          
          {/* People List */}
          {(filterType === 'particular' || filterType === 'exclude') && (
            <div className="bg-white p-3 sm:p-4 rounded-lg border mx-2 sm:mx-0">
              <h3 className="text-base sm:text-lg font-medium text-gray-900 mb-3 sm:mb-4">
                {filterType === 'particular' ? 'Select People to Send' : 'Select People to Exclude'}
              </h3>
              <div className="space-y-1 sm:space-y-2 max-h-48 sm:max-h-60 overflow-y-auto">
                {people.map((person, index) => (
                  <label key={index} className="flex items-start sm:items-center p-2 hover:bg-gray-50 rounded cursor-pointer">
                    <input 
                      type="checkbox"
                      checked={filterType === 'exclude' ? !selectedPeople.includes(person.email) : selectedPeople.includes(person.email)}
                      onChange={() => handlePersonToggle(person.email)}
                      className="mr-2 sm:mr-3 mt-1 sm:mt-0 flex-shrink-0"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm sm:text-base break-words">
                        <span className="block sm:inline">{person.name || 'No Name'}</span>
                        <span className="block sm:inline text-gray-600 text-xs sm:text-sm mt-1 sm:mt-0">
                          {person.email ? ` (${person.email})` : ' (No Email)'}
                        </span>
                      </div>
                      <div className="text-xs sm:text-sm text-gray-500 break-words">{person.company || 'No Company'}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}
          
          {/* Send Button */}
          <div className="flex justify-center px-2 sm:px-0 pb-4 sm:pb-0">
            <button 
              onClick={handleSendEmail}
              className="w-full sm:w-auto px-4 sm:px-8 py-3 text-sm sm:text-base bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium max-w-sm"
            >
              Send Email to {selectedPeople.length} recipient(s)
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default EmailPage;