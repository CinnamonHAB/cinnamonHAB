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
end
