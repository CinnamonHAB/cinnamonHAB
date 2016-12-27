class RestController < ApplicationController
  def openhab_getitems
  	require 'net/http'

  	uri = URI.parse('http://localhost/rest/items')
  	req = Net::HTTP::Get.new(uri.to_s)
  	res = Net::HTTP.start(uri.host, uri.port) {|http|
  	  http.request(req)
  	}
    render json: res.body
	end
  def openhab_getstate
    require 'net/http'
    require 'uri'

    item = "#{request.body.read}" 
    uri = URI.parse('http://localhost/rest/items/'+item+'/state')
    req = Net::HTTP::Put.new(uri.to_s)
    res = Net::HTTP.start(uri.host, uri.port) {|http|
      http.request(req)
    }
    render plain: res.body
  end
  def openhab_updatestate
    require 'net/http'
    require 'uri'

    data = "#{request.body.read}" 
    dataArray = data.split(' ')
    item = dataArray[0]
    newState = dataArray[1]
    uri = URI.parse('http://localhost/rest/items/'+item+'/state')
    req = Net::HTTP::Put.new(uri.to_s,{'Content-Type' => 'text/plain'})
    req.body = newState
    res = Net::HTTP.start(uri.host, uri.port) {|http|
      http.request(req)
    }
    render plain: res.code
  end
  def openhab_sendcommand
    require 'net/http'
    require 'uri'

  	data = "#{request.body.read}"  	
  	dataArray = data.split(' ')
  	item = dataArray[0]
  	command = dataArray[1]
  	uri = URI.parse('http://localhost/rest/items/'+item)
  	req = Net::HTTP::Post.new(uri.to_s, {'Content-Type' => 'text/plain'})
  	req.body = command
    res = Net::HTTP.start(uri.host, uri.port) {|http|
      http.request(req)
    }
    render plain: res.code
  end
  
  def openhab_addItem
    require 'net/http'
    require 'uri'

    data = "#{request.body.read}" 
    
    uri = URI.parse('http://localhost/rest/items/')
    req = Net::HTTP::Put.new(uri.to_s,{'Content-Type' => 'text/plain'})
    req.body = data
    res = Net::HTTP.start(uri.host, uri.port) {|http|
      http.request(req)
    }
    render plain: res.code
  end

  def openhab_deleteItem
    require 'net/http'
    require 'uri'
    
    data = "#{request.body.read}" 
    dataArray = data.split(' ')
    item = dataArray[0]
    
    uri = URI.parse('http://localhost/rest/items/'+item+'/')
    
    req = Net::HTTP::Delete.new(uri.to_s)
    
    res = Net::HTTP.start(uri.host, uri.port) {|http|
      http.request(req)
    }
    render plain: res.code
  end

  def openhab_getItem
    require 'net/http'
    
    data = "#{request.body.read}" 
    dataArray = data.split(' ')
    item = dataArray[0]
    
  	uri = URI.parse('http://localhost/rest/items'+item+'/')
  	req = Net::HTTP::Get.new(uri.to_s)
  	res = Net::HTTP.start(uri.host, uri.port) {|http|
  	  http.request(req)
  	}
    render json: res.body
  end

  def openhab_addItemToGroup
    require 'net/http'
    require 'uri'

    data = "#{request.body.read}" 
    dataArray = data.split(' ')
    groupName = dataArray[0]
    memberName = dataArray[1]
    
    uri = URI.parse('http://localhost/rest/items/'+groupName+'/')
    req = Net::HTTP::Put.new(uri.to_s,{'Content-Type' => 'text/plain'})
    req.body = memberName
    res = Net::HTTP.start(uri.host, uri.port) {|http|
      http.request(req)
    }
    render plain: res.code
 end

 def openhab_removeItemFromGroup
   require 'net/http'
   require 'uri'
    
   data = "#{request.body.read}" 
   dataArray = data.split(' ')
   groupName = dataArray[0]
   item = dataArray[1]
    
   uri = URI.parse('http://localhost/rest/items/'+groupName+'/'+item+'/')
    
   req = Net::HTTP::Delete.new(uri.to_s)
    
   res = Net::HTTP.start(uri.host, uri.port) {|http|
     http.request(req)
   }
   render plain: res.code
 end

 def openhab_addTagToItem
   require 'net/http'
   require 'uri'

   data = "#{request.body.read}" 
   dataArray = data.split(' ')
   item = dataArray[0]
   tag = dataArray[1]
        
   uri = URI.parse('http://localhost/rest/items/'+item+'/')
   req = Net::HTTP::Put.new(uri.to_s,{'Content-Type' => 'text/plain'})
   req.body = tag
   res = Net::HTTP.start(uri.host, uri.port) {|http|
     http.request(req)
   }
   render plain: res.code
 end

 def openhab_removeTagFromItem
   require 'net/http'
   require 'uri'
    
   data = "#{request.body.read}" 
   dataArray = data.split(' ')
   item = dataArray[0]
   tag = dataArray[1]
    
   uri = URI.parse('http://localhost/rest/items/'+item+'/'+tag+'/')
    
   req = Net::HTTP::Delete.new(uri.to_s)
    
   res = Net::HTTP.start(uri.host, uri.port) {|http|
     http.request(req)
   }
   render plain: res.code
 end
end
