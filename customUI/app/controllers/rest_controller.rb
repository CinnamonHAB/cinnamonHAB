class RestController < ApplicationController
  def openhab_getitems
  	require 'net/http'

	url = URI.parse('http://localhost/rest/items')
	req = Net::HTTP::Get.new(url.to_s)
	res = Net::HTTP.start(url.host, url.port) {|http|
	  http.request(req)
	}
  render json: res.body
	end
  def openhab_sendcommand
  	data = "#{request.body.read}"
  	
  	dataArray = data.split(' ')
  	item = dataArray[0]
  	command = dataArray[1]
  	require 'net/http'

	url = URI.parse("http://localhost/rest/items/"+item)
	http = Net::HTTP.new(url.host, url.port)
	req = Net::HTTP::POST.new(url.path, {'Content-Type' => 'text/plain'})
	req.body = command
	res = http.request(req)
  render text: res
  end
end
