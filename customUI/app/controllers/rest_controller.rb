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
  def openhab_sendcommand
    require 'net/http'
    require 'uri'

  	data = "#{request.body.read}"  	
  	dataArray = data.split(' ')
  	item = dataArray[0]
  	command = dataArray[1]
  	header = { 'Content-Type': 'text/plain'}
  	uri = URI.parse('http://localhost/rest/items/'+item)
  	req = Net::HTTP::Post.new(uri.to_s, header)
  	req.body = command
    
    res = Net::HTTP.start(uri.host, uri.port) {|http|
      http.request(req)
    }
    puts res.code
    render plain: res
  end
end
